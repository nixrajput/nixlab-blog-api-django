from django.contrib import admin
from django.contrib.admin import site

from blog.models import BlogPost, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    max_num = 1


class BlogPostAdmin(admin.ModelAdmin):
    model = BlogPost
    readonly_fields = ["date_published", "last_updated"]
    list_display = ["id", "author", "date_published"]
    search_fields = ["slug", "title", "author"]

    inlines = [PostImageInline]


class PostImageAdmin(admin.ModelAdmin):
    model = PostImage
    readonly_fields = ["date_added", "last_updated"]
    list_display = ["id", "post", "date_added"]


site.register(BlogPost, BlogPostAdmin)
site.register(PostImage, PostImageAdmin)
