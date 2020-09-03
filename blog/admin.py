from django.contrib import admin
from django.contrib.admin import site

from blog.models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    model = BlogPost
    list_display = ["title", "author", "date_published"]


site.register(BlogPost, BlogPostAdmin)
