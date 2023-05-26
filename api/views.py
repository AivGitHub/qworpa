from django.core.exceptions import PermissionDenied
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from blogs.models import Post, PostComment, PostCommentLike, PostLike


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


@api_view(['DELETE'])
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

    def get_author(self, post):
        return {
            'full_name': post.author.get_full_name(),
        }

    def get_likes_amount(self, post):
        return post.likes.count()

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
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_post_comment(request, *args, **kwargs):
    post = process_add_post_comment(request, kwargs)
    serializer = PostCommentResponseSerializer(post)
    return Response(serializer.data, status.HTTP_200_OK)
