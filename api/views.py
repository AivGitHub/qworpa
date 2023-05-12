from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from blogs.models import Post, PostLike


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
