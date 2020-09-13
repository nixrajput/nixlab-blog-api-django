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
    AccountDetailSerializer,
    ProfilePictureUploadSerializer
)
from account.utils import token_expire_handler, expires_in

DOES_NOT_EXIST = "DOES_NOT_EXIST"
EMAIL_EXISTS = "EMAIL_EXISTS"
USERNAME_EXISTS = "USERNAME_EXISTS"
INVALID_EMAIL = "INVALID_EMAIL"
INVALID_USERNAME = "INVALID_USERNAME"
SUCCESS_TEXT = "SUCCESSFULLY_AUTHENTICATED"
CREATION_TEXT = "SUCCESSFULLY_CREATED"
INVALID_PASSWORD = "INVALID_PASSWORD"
UPDATE_TEXT = "SUCCESSFULLY_UPDATED"
UPLOAD_SUCCESS = "SUCCESSFULLY_UPLOADED"


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def registration_view(request):
    if request.method == "POST":
        data = {}
        email = request.data.get('email', '0')
        if validate_email(email) is not None:
            data['response'] = "Error"
            data['error_message'] = EMAIL_EXISTS
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username', '0')
        if validate_username(username) is not None:
            data['response'] = "Error"
            data['error_message'] = USERNAME_EXISTS
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()
            data['response'] = CREATION_TEXT
            data['id'] = account.id
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['timestamp'] = account.timestamp
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
            context['error_message'] = INVALID_USERNAME
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        if validate_password(username, password) is False:
            context['response'] = "Error"
            context['error_message'] = INVALID_PASSWORD
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            account = authenticate(username=username, password=password)

            try:
                token, _ = Token.objects.get_or_create(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)

            is_expired, token = token_expire_handler(token)

            context['response'] = SUCCESS_TEXT
            context['id'] = account.id
            context['token'] = token.key
            context['expires_in'] = expires_in(token)
            return Response(context, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def detail_user_view(request, user_id):
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        return Response({'response': DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = AccountDetailSerializer(user)

    if request.method == "GET":
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'response': serializer.errors, },
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def api_follow_toggle_view(request, user_id):
    try:
        user = Account.objects.get(id=request.user.id)
        following_user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        return Response({'response': DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND)

    if request.user.is_authenticated:
        if following_user in user.following.all() and \
                request.user in following_user.followers.all():
            user.following.remove(following_user)
            following_user.followers.remove(request.user)
            is_following = False
        else:
            user.following.add(following_user)
            following_user.followers.add(request.user)
            is_following = True

        updated = True

        data = {
            "follower": user.username,
            "following": following_user.username,
            "updated": updated,
            "is_following": is_following
        }

        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def api_check_if_following_view(request, user_id):
    try:
        user = Account.objects.get(id=request.user.id)
        following_user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        return Response({'response': DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND)

    if request.user.is_authenticated:
        if following_user in user.following.all() and \
                request.user in following_user.followers.all():
            is_following = True
        else:
            is_following = False

        data = {
            "follower": user.username,
            "following": following_user.username,
            "is_following": is_following
        }

        return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def upload_profile_picture(request):
    if request.method == "POST":

        data = request.data
        data['user'] = request.user.id
        serializer = ProfilePictureUploadSerializer(data=data)

        data = {}
        if serializer.is_valid():
            profile_pic = serializer.save()
            data['response'] = UPLOAD_SUCCESS
            data['id'] = profile_pic.id
            data['image'] = profile_pic.image.url
            data['user'] = profile_pic.user.username
            data['timestamp'] = profile_pic.timestamp
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def update_account_view(request):
    try:
        account = request.user
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = AccountPropertiesSerializer(account, data=request.data, partial=True)
        data = {}

        if serializer.is_valid():
            serializer.save()
            data['response'] = UPDATE_TEXT
            data['username'] = account.username
            data['email'] = account.email
            data['phone'] = account.phone
            data['dob'] = account.dob
            data['timestamp'] = account.timestamp
            return Response(data=data, status=status.HTTP_200_OK)
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
            if account:
                data['response'] = email
        except Account.DoesNotExist:
            data['response'] = DOES_NOT_EXIST
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
            data['response'] = DOES_NOT_EXIST
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
        raise ValueError(DOES_NOT_EXIST)

    if account.check_password(password):
        return True
    else:
        return False
