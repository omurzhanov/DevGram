from django.urls import path
from .views import post_comment_create_and_list_view, like_unlike_post, PostDeleteView, PostUpdateView, favourite_add, favourites_list, newest_posts

urlpatterns = [
    path('myfeed/', post_comment_create_and_list_view, name='main-post-view'),
    path('', newest_posts, name='newest-post-view'),
    path('liked/', like_unlike_post, name='like-post-view'),
    path('<pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('<pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('fav/<int:id>/', favourite_add, name='favourite-add'),
    path('favourites/',favourites_list, name='favourites-list')
]