from django.urls import path

from chats.views import (
    ApiUserChatListView,
)

app_name = "chats"

urlpatterns = [
    path('detail/<uid>/', ApiUserChatListView.as_view(), name='chat_detail'),
]
