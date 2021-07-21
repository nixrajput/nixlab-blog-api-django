from django.urls import path

from blog.views import (
    api_detail_blog_view,
    api_create_blog_view,
    api_update_blog_view,
    api_delete_blog_view,
    ApiBlogListView,
    ApiUserBlogListView,
    api_is_author_of_blogpost,
    api_like_toggle_view,
)

urlpatterns = [
    path('', ApiBlogListView.as_view(), name="list"),
    path('list/<uid>/', ApiUserBlogListView.as_view(), name='post_list'),
    path('create/', api_create_blog_view, name="create"),
    path('<slug>/', api_detail_blog_view, name="detail"),
    path('<slug>/update/', api_update_blog_view, name="update"),
    path('<slug>/delete/', api_delete_blog_view, name="delete"),
    path('<slug>/like/', api_like_toggle_view, name="like"),
    path('<slug>/is_author/', api_is_author_of_blogpost, name="is_author"),
]
