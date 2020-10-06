from django.contrib import admin
from django.contrib.admin import site

from chats.models import Chats


class ChatAdmin(admin.ModelAdmin):
    model = Chats
    search_fields = ['message', 'user__username']


site.register(Chats, ChatAdmin)
