from django.contrib import admin
from django.contrib.admin import site

from blog.models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    model = BlogPost
    readonly_fields = ["date_published", "last_updated"]
    list_display = ["id", "author", "date_published"]
    search_fields = ["slug", "title", "author"]


site.register(BlogPost, BlogPostAdmin)
