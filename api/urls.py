from django.urls import path

from api.views import (
    add_post_comment,
    change_password,
    delete_post,
    delete_post_comment,
    PostCommentsView,
    PostNestedCommentsView,
    toggle_post_comment_like,
    toggle_post_like,
)

urlpatterns = [
    path('v1/posts/<str:url_hex>/likes/toggle/', toggle_post_like, name='toggle-post-like'),
    path('v1/posts/<str:url_hex>/delete/', delete_post, name='delete-post'),
    path(
        'v1/posts/<str:url_hex>/comments/<int:comment_id>/likes/toggle/',
        toggle_post_comment_like,
        name='toggle-post-comment-like'
    ),
    path('v1/posts/<str:url_hex>/comments/add/', add_post_comment, name='add-post-comment'),
    path('v1/posts/<str:url_hex>/comments/', PostCommentsView.as_view(), name='comment-list'),
    path(
        'v1/posts/<str:url_hex>/comments/<int:comment_id>/',
        PostNestedCommentsView.as_view(),
        name='nested-comment-list'
    ),
    path(
        'v1/posts/<str:url_hex>/comments/<int:comment_id>/delete/',
        delete_post_comment,
        name='delete-post-comment'
    ),
    path(
        'v1/accounts/settings/passwords/change/',
        change_password,
        name='change-password'
    ),
]
