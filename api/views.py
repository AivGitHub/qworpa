from django.contrib.auth import update_session_auth_hash
import django.contrib.auth.password_validation as validators
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter
from django.core.exceptions import PermissionDenied
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from blogs.models import Post, PostComment, PostCommentLike, PostLike
from crypto.models import Message


def _get_post_from_payload(payload: dict, user: User):
    try:
        url_hex = payload['url_hex']
    except KeyError:
        raise PermissionDenied()
    try:
        post: Post = Post.objects.get(url_hex=url_hex)
    except Post.DoesNotExist:
        raise PermissionDenied()

    if user != post.author and post.is_draft:
        raise PermissionDenied()
    return post


def process_toggle_post_like(user: User, payload: dict):
    post = _get_post_from_payload(payload, user)
    try:
        post_like = PostLike.objects.get(user=user, post=post)
    except PostLike.DoesNotExist:
        PostLike.objects.create(user=user, post=post)
    else:
        post_like.delete()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, *args, **kwargs):
    process_toggle_post_like(request.user, kwargs)
    return Response(status=status.HTTP_200_OK)


def process_delete_post(user: User, payload: dict):
    post = _get_post_from_payload(payload, user)
    if post.author != user:
        raise PermissionDenied()
    post.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_post(request, *args, **kwargs):
    process_delete_post(request.user, kwargs)
    return Response(status=status.HTTP_200_OK)


def _get_comment_from_payload(payload: dict, user: User):
    try:
        comment_id = payload['comment_id']
    except KeyError:
        raise PermissionDenied()
    # Check that user makes a request from a page with post.
    # Can be removed for now to optimise the request.
    post = _get_post_from_payload(payload, user)
    try:
        post_comment: PostComment = post.comments.get(id=comment_id)
    except PostComment.DoesNotExist:
        raise PermissionDenied()

    return post_comment


def process_toggle_post_comment_like(user: User, payload: dict):
    post_comment: PostComment = _get_comment_from_payload(payload, user)
    try:
        post_comment_like = PostCommentLike.objects.get(user=user, comment=post_comment)
    except PostCommentLike.DoesNotExist:
        PostCommentLike.objects.create(user=user, comment=post_comment)
    else:
        post_comment_like.delete()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_comment_like(request, *args, **kwargs):
    process_toggle_post_comment_like(request.user, kwargs)
    return Response(status=status.HTTP_200_OK)


def _get_comment_body_from_request(request):
    try:
        return request.POST['content']
    except MultiValueDictKeyError:
        raise PermissionDenied()


def _get_parent_comment(request):
    try:
        comment_id = request.POST['parent_comment_id']
    except MultiValueDictKeyError:
        return None
    try:
        return PostComment.objects.get(id=comment_id)
    except PostComment.DoesNotExist:
        raise PermissionDenied()


def process_add_post_comment(request, payload: dict):
    content = _get_comment_body_from_request(request)
    post = _get_post_from_payload(payload, request.user)
    args = dict(post=post, author=request.user, content=content)

    parent_comment = _get_parent_comment(request)
    if parent_comment is not None:
        args.update(parent=parent_comment)
    return PostComment.objects.create(**args)


class PostCommentResponseSerializer(serializers.ModelSerializer):
    url_hex = serializers.CharField(source='post.url_hex')
    likes_amount = serializers.SerializerMethodField(read_only=True)
    author = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    has_add_permission = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    has_delete_permission = serializers.SerializerMethodField()

    def get_created_at(self, post_comment):
        return NaturalTimeFormatter.string_for(post_comment.created_at)

    def get_author(self, post):
        return {
            'full_name': post.author.get_safe_full_name(),
        }

    def get_likes_amount(self, post_comment):
        return post_comment.likes.count()

    def get_has_liked(self, post_comment):
        try:
            user = self.context['request'].user
        except KeyError:
            return False
        if user.is_anonymous:
            return False
        try:
            post_comment.likes.get(user=user)
        except PostCommentLike.DoesNotExist:
            return False
        return True

    def get_has_add_permission(self, post_comment):
        try:
            user = self.context['request'].user
        except KeyError:
            return False
        if user.is_anonymous:
            return False
        return True

    def get_has_delete_permission(self, post_comment):
        try:
            user = self.context['request'].user
        except KeyError:
            return False
        return post_comment.has_delete_permission(user)

    class Meta:
        model = PostComment
        fields = (
            'id',
            'url_hex',
            'parent',
            'created_at',
            'likes_amount',
            'content',
            'author',
            'has_liked',
            'has_add_permission',
            'has_delete_permission',
        )


class PostCommentRequestSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=3, max_length=256)

    class Meta:
        model = PostComment
        fields = (
            'content',
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_post_comment(request, *args, **kwargs):
    serializer_request = PostCommentRequestSerializer(data=request.POST)
    serializer_request.is_valid(raise_exception=True)
    post = process_add_post_comment(request, kwargs)
    serializer = PostCommentResponseSerializer(post, context={'request': request})
    return Response(serializer.data, status.HTTP_200_OK)


class Pagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'p'


class PostCommentsView(generics.ListAPIView):
    serializer_class = PostCommentResponseSerializer
    page_size_query_param = 'page_size'
    pagination_class = Pagination

    def get_queryset(self):
        post = _get_post_from_payload(self.kwargs, self.request.user)
        return post.comments.all().order_by('-id')


class PostNestedCommentsView(generics.ListAPIView):
    serializer_class = PostCommentResponseSerializer
    page_size_query_param = 'page_size'
    pagination_class = Pagination

    def get_queryset(self):
        comment_id = self.kwargs['comment_id']
        post = _get_post_from_payload(self.kwargs, self.request.user)
        try:
            parent_comment = post.comments.get(id=comment_id)
        except PostComment.DoesNotExist:
            raise PermissionDenied()
        return parent_comment.nested_comments.all()


def process_delete_post_comment(user: User, payload):
    post_comment: PostComment = _get_comment_from_payload(payload, user)
    if not post_comment.has_delete_permission(user):
        raise PermissionDenied()
    post_comment.delete()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_post_comment(request, *args, **kwargs):
    process_delete_post_comment(request.user, kwargs)
    return Response(status=status.HTTP_200_OK)


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_old_password(self, password):
        try:
            user = self.context['user']
        except KeyError:
            raise PermissionDenied()
        if not user.check_password(password):
            raise serializers.ValidationError(_('Wrong password. Check password and try again.'))
        return password

    def validate(self, attrs):
        try:
            user = self.context['user']
        except KeyError:
            raise PermissionDenied()
        password = attrs['new_password1']
        if password != attrs['new_password2']:
            raise serializers.ValidationError(_("Passwords don't match"))
        validators.validate_password(password=password, user=user)
        return attrs


def process_change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
    serializer.is_valid(raise_exception=True)
    request.user.set_password(serializer.data['new_password1'])
    request.user.save(update_fields=['password'])
    update_session_auth_hash(request, request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request, *args, **kwargs):
    process_change_password(request)
    return Response({}, status=status.HTTP_200_OK)


def get_user_from_payload(payload):
    try:
        user_id = payload['user_id']
    except KeyError:
        raise PermissionDenied()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise PermissionDenied()


def process_toggle_subscription(request):
    user = get_user_from_payload(request.POST)
    if user == request.user:
        raise PermissionDenied()
    if user.subscribers.contains(request.user):
        user.subscribers.remove(request.user)
    else:
        user.subscribers.add(request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_subscription(request, *args, **kwargs):
    process_toggle_subscription(request)
    return Response({}, status=status.HTTP_200_OK)


class CryptoMessageRequestSerializer(serializers.ModelSerializer):
    text = serializers.CharField(min_length=1, max_length=32000)

    class Meta:
        model = Message
        fields = (
            "hex",
            "text",
        )


def process_add_crypto_message(data):
    serializer = CryptoMessageRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


@api_view(["POST"])
def add_crypto_message(request, *args, **kwargs):
    data = process_add_crypto_message(request.data)
    return Response(data, status=status.HTTP_201_CREATED)


class CryptoMessagesView(generics.ListAPIView):
    serializer_class = CryptoMessageRequestSerializer
    page_size_query_param = 'page_size'
    pagination_class = Pagination

    def get_queryset(self):
        return Message.objects.all().order_by('-id')
