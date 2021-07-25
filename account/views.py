import smtplib

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
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
from account.tokens import user_tokenizer
from account.utils import token_expire_handler, expires_in
from blog.utils import validate_uuid4

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
            data['response'] = "error"
            data['message'] = "Email is already in use."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username', '0')
        if validate_username(username) is not None:
            data['response'] = "error"
            data['message'] = "Username is already in use."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save(commit=False)

            token = user_tokenizer.make_token(account)
            user_id = urlsafe_base64_encode(force_bytes(account.id))

            if settings.DEBUG:
                domain = "http://127.0.0.1:8000"
            else:
                domain = "https://nixlab-blog-api.herokuapp.com"

            url = domain + reverse('account_verification', kwargs={
                'user_id': user_id,
                'token': token
            })

            message = get_template('verify_user.html').render({
                'url': url,
                'first_name': account.first_name,
                'last_name': account.last_name
            })

            subject = 'Confirm Your Account - NixLab'

            try:
                res = send_mail(
                    auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD,
                    subject=subject,
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[account.email],
                    html_message=message
                )

                account.save()

                data['response'] = "account_created"
                data['mail_response'] = 'success'
                data['mail_result'] = res
                data['message'] = "Registration successful. A verification email has been sent to your email. Please " \
                                  "verify your account to complete registration. If you don't receive an email, " \
                                  "please make sure you've entered the address you registered with, and check your " \
                                  "spam folder."
                return Response(data, status=status.HTTP_201_CREATED)
            except (smtplib.SMTPException, TimeoutError) as exc:
                data["response"] = "error"
                data['mail_response'] = 'error'
                data['message'] = "An error occurred while sending verification email. Please check your email " \
                                  "address and try again."
                data['error'] = str(exc)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        else:
            data["response"] = "error"
            data["message"] = serializer.errors.__str__()
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


def verify_account(request, user_id, token):
    data = {}

    try:
        user_id = force_text(urlsafe_base64_decode(user_id))
        user = Account.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and user_tokenizer.check_token(user, token):
        user.is_valid = True
        user.save()
        data['response'] = 'success'
        data['message'] = 'Verification successful. Please login to your account.'
    else:
        data['response'] = 'error'
        data['message'] = 'An error occurred while verifying your account. Please try to request a new ' \
                          'verification email.'
    return render(request, 'success.html', {'data': data})


class ObtainAuthTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        data = {}

        serializer = LoginSerializer(data=request.data)

        username = request.data.get('username', '0')
        password = request.data.get('password', '0')

        if validate_username(username) is None:
            data['response'] = "error"
            data['message'] = "Your username is incorrect."
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if validate_password(username, password) is False:
            data['response'] = "error"
            data['message'] = "Your password is incorrect."
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            account = authenticate(username=username, password=password)

            if account.is_valid:
                try:
                    token, _ = Token.objects.get_or_create(user=account)
                except Token.DoesNotExist:
                    token = Token.objects.create(user=account)

                is_expired, token = token_expire_handler(token)

                data['response'] = "success"
                data["message"] = "Login successful."
                data['id'] = account.id
                data['token'] = token.key
                data['expires_in'] = expires_in(token)
                return Response(data, status=status.HTTP_200_OK)
            else:
                data['response'] = "error"
                data['message'] = "Your account is not verified. Please verify your account and try again."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data['response'] = "error"
        data["message"] = serializer.errors.__str__()
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
def detail_user_view(request, user_id):
    data = {}

    is_uuid = validate_uuid4(user_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "User ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        data["response"] = "error"
        data["message"] = "User not found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    serializer = AccountDetailSerializer(user)

    if request.method == "GET":
        return Response(serializer.data, status=status.HTTP_200_OK)
    data["response"] = "error"
    data["message"] = serializer.errors
    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
def api_follow_toggle_view(request, user_id):
    data = {}

    is_uuid = validate_uuid4(user_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "User ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Account.objects.get(id=request.user.id)
        following_user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        data["response"] = "error"
        data["message"] = "User not found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_authenticated:
        if following_user in user.following.all() and request.user in following_user.followers.all():
            user.following.remove(following_user)
            following_user.followers.remove(request.user)
            is_following = False
        else:
            user.following.add(following_user)
            following_user.followers.add(request.user)
            is_following = True

        updated = True

        data["response"] = "success"
        data["follower"] = user.username
        data["following"] = following_user.username,
        data["updated"] = updated
        data["is_following"] = is_following
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data["response"] = "error"
        data["message"] = "User is not authenticated."
        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
def api_check_if_following_view(request, user_id):
    data = {}

    is_uuid = validate_uuid4(user_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "User ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Account.objects.get(id=request.user.id)
        following_user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        data["response"] = "error"
        data["message"] = "User not found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_authenticated:
        if following_user in user.following.all() and \
                request.user in following_user.followers.all():
            is_following = True
        else:
            is_following = False

        data["response"] = "success"
        data["follower"] = user.username
        data["following"] = following_user.username,
        data["is_following"] = is_following
        return Response(data, status=status.HTTP_200_OK)
    else:
        data["response"] = "error"
        data["message"] = "User is not authenticated."
        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
def upload_profile_picture_view(request):
    if request.method == "POST":
        req_data = request.data
        req_data['user'] = request.user.id
        serializer = ProfilePictureUploadSerializer(data=req_data)

        data = {}
        if serializer.is_valid():
            profile_pic = serializer.save()
            data['response'] = "success"
            data["message"] = "Profile picture uploaded."
            data['id'] = profile_pic.id
            data['user_id'] = profile_pic.user.id
            data['uploaded_at'] = profile_pic.uploaded_at
            return Response(data=data, status=status.HTTP_200_OK)
        data["response"] = "error"
        data["message"] = serializer.errors.__str__()
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
def update_account_view(request):
    data = {}

    try:
        account = request.user
    except Account.DoesNotExist:
        data["response"] = "error"
        data["message"] = "User not found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = AccountPropertiesSerializer(account, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            data['response'] = "success"
            data["message"] = "User details updated."
            data["user_id"] = account.id
            data['last_updated'] = account.last_updated
            return Response(data=data, status=status.HTTP_200_OK)

        else:
            data["response"] = "error"
            data["message"] = serializer.errors.__str__()
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def is_account_complete_view(request):
    data = {}

    try:
        account = request.user
    except Account.DoesNotExist:
        data["response"] = "error"
        data["message"] = "User not found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if account.first_name is None or \
                account.last_name is None or \
                account.dob is None or \
                account.about is None or \
                account.gender is None:
            data['response'] = "success"
            data['uid'] = account.id
            data['is_complete'] = False
            data["message"] = "User profile setup is not complete."
            return Response(data, status=status.HTTP_200_OK)
        else:
            data['response'] = "success"
            data['uid'] = account.id
            data['is_complete'] = True
            data["message"] = "User profile setup is complete."
            return Response(data, status=status.HTTP_200_OK)


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
@authentication_classes([TokenAuthentication])
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
