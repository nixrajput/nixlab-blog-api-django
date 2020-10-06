from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from chats.models import Chats
from chats.serializers import ChatSerializer

DOES_NOT_EXIST = "DOES_NOT_EXIST"


class ApiUserChatListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = ChatSerializer
    lookup_url_kwarg = "uid"

    def get_queryset(self, *args, **kwargs):
        uid = self.kwargs.get(self.lookup_url_kwarg)
        queryset = Chats.objects.filter(user=uid).order_by('-sent_at')

        return queryset
