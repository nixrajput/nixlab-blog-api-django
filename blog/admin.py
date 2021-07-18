from django.contrib import admin
from django.contrib.admin import site

from blog.models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    model = BlogPost
    list_display = ["slug", "author", "date_published"]
    search_fields = ["slug", "body", "author"]


site.register(BlogPost, BlogPostAdmin)
