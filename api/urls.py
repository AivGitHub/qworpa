from django.urls import path

from api.views import delete_post, toggle_post_comment_like, toggle_post_like

urlpatterns = [
    path('v1/posts/<str:url_hex>/likes/toggle/', toggle_post_like, name='toggle-post-like'),
    path('v1/posts/<str:url_hex>/delete/', delete_post, name='delete-post'),
    path(
        'v1/posts/<str:url_hex>/comments/<int:comment_id>/likes/toggle/',
        toggle_post_comment_like,
        name='toggle-post-comment-like'
    ),
]
