from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Account
from account.serializers import RegistrationSerializer, AccountPropertiesSerializer


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def registration_view(request):
    if request.method == "POST":
        data = {}
        email = request.data.get('email', '0')
        if validate_email(email) is not None:
            data['response'] = "Error"
            data['error_message'] = "This email is already in use."
            return Response(data)

        username = request.data.get('username', '0')
        if validate_username(username) is not None:
            data['response'] = "Error"
            data['error_message'] = "This username is already in use."
            return Response(data)

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "Successfully registered a new user."
            data['id'] = account.id
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.get(user=account).key
            data['token'] = token
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


def validate_email(email):
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return None
    if account is not None:
        return email


def validate_username(username):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None
    if account is not None:
        return username


@api_view(["GET", "PUT"])
@permission_classes((IsAuthenticated,))
def update_account_view(request):
    try:
        account = request.user
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        user = Account.objects.get(username=request.user.username)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = AccountPropertiesSerializer(user)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = AccountPropertiesSerializer(account, data=request.data)
        data = {}

        if serializer.is_valid():
            serializer.save()
            data["response"] = "Account updated!"
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainAuthTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)

            context['response'] = 'Successfully authenticated!'
            context['id'] = user.pk
            context['username'] = username
            context['token'] = token.key
            return Response(context, status=status.HTTP_200_OK)
        else:
            context['response'] = 'Error'
            context['error_message'] = 'Invalid credentials!'
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
