from django.urls import path

from blogs.views import FavoritesListView, MyPostListView, PostCreateView, PostDetailsView, PostEditView, PostListView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('posts/<str:url_hex>/', PostDetailsView.as_view(), name='post-details'),
    path('posts/<str:url_hex>/edit/', PostEditView.as_view(), name='edit-post'),
    path('post/add/', PostCreateView.as_view(), name='add-post'),
    path('im/', MyPostListView.as_view(), name='my-post-list'),
    path('favorites/', FavoritesListView.as_view(), name='favorites'),
]
