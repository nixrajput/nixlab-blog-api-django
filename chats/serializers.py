from rest_framework.serializers import ModelSerializer

from chats.models import Chats


class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chats
        fields = "__all__"
