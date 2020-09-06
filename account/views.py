from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Account
from account.serializers import (
    RegistrationSerializer,
    AccountPropertiesSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
)


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
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username', '0')
        if validate_username(username) is not None:
            data['response'] = "Error"
            data['error_message'] = "This username is already in use."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

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


class ObtainAuthTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):

        context = {}

        serializer = LoginSerializer(data=request.data)

        username = request.data.get('username', '0')
        password = request.data.get('password', '0')

        if validate_username(username) is None:
            context['response'] = "Error"
            context['error_message'] = "Username is incorrect."
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        if validate_password(username, password) is False:
            context['response'] = "Error"
            context['error_message'] = "Password is incorrect."
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            account = authenticate(username=username, password=password)

            try:
                token = Token.objects.get(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)
            context['response'] = 'Successfully authenticated!'
            context['id'] = account.id
            context['username'] = serializer.data['username']
            context['token'] = token.key
            return Response(context, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    if request.method == "PUT":
        serializer = AccountPropertiesSerializer(account, data=request.data)
        data = {}

        if serializer.is_valid():
            serializer.save()
            data['response'] = 'Account update success'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def does_account_exist_view(request):
    if request.method == 'GET':
        email = request.GET['email']
        data = {}
        try:
            account = Account.objects.get(email=email)
            data['response'] = email
        except Account.DoesNotExist:
            data['response'] = "Account does not exist"
        return Response(data)


@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def does_account_exist_view(request):

    if request.method == 'GET':
        email = request.GET['email'].lower()
        data = {}
        try:
            account = Account.objects.get(email=email)
            data['response'] = email
        except Account.DoesNotExist:
            data['response'] = "Account does not exist"
        return Response(data)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = Account
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # confirm the new passwords match
            new_password = serializer.data.get("new_password")
            confirm_new_password = serializer.data.get("confirm_new_password")
            if new_password != confirm_new_password:
                return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"response": "successfully changed password"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def account_properties_view(request):

    try:
        account = request.user
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountPropertiesSerializer(account)
        return Response(serializer.data)


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


def validate_password(username, password):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        raise ValueError("Account does not exist.")

    if account.check_password(password):
        return True
    else:
        return False
