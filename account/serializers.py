import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    Serializer,
    SerializerMethodField,
)

from account.models import Account, ProfilePicture
from blog.utils import is_image_aspect_ratio_valid, is_image_size_valid

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2
DOES_NOT_EXIST = "DOES_NOT_EXIST"


class RegistrationSerializer(ModelSerializer):
    password2 = CharField(style={"input_type": 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ["email", "username", "password", "password2", "timestamp"]
        extra_kwargs = {"password2": {"write_only": True}}

    def save(self, **kwargs):
        account = Account(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            timestamp=self.validated_data['timestamp'],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise ValidationError({"error_response": "password doesn't matched."})
        account.set_password(password)
        account.save()
        return account


class LoginSerializer(Serializer):
    username = CharField(required=True)
    password = CharField(required=True)


class ProfilePictureSerializer(ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ['image']


class ProfilePictureUploadSerializer(ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ['user', 'image', 'timestamp']

    def save(self):

        try:
            image = self.validated_data['image']
            timestamp = self.validated_data['timestamp']

            profile_pic = ProfilePicture(
                user=self.validated_data['user'],
                image=image,
                timestamp=timestamp,
            )

            url = os.path.join(settings.TEMP, str(image))
            storage = FileSystemStorage(location=url)

            with storage.open('', 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
                destination.close()

            if not is_image_size_valid(url, IMAGE_SIZE_MAX_BYTES):
                os.remove(url)
                raise ValidationError({
                    "response": "The image is too large. Image must be less than 2 MB."
                })

            if not is_image_aspect_ratio_valid(url):
                os.remove(url)
                raise ValidationError({
                    "response": "Image must be in square pixels."
                })

            os.remove(url)
            profile_pic.save()
            return profile_pic

        except KeyError:
            raise ValidationError({
                "response": "You must have all the fields not null."
            })


class AccountDetailSerializer(ModelSerializer):
    profile_picture = SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id', 'first_name', 'last_name', 'phone',
            'username', 'email', 'dob', 'profile_picture',
        ]

    def get_profile_picture(self, obj):
        try:
            image = ProfilePicture.objects.filter(user=obj.id).order_by('-uploaded_at')[0]
        except (ProfilePicture.DoesNotExist, IndexError):
            image = ""

        serializer = ProfilePictureSerializer(image)

        return serializer.data


class AccountPropertiesSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone", "dob", "timestamp"]


class ChangePasswordSerializer(Serializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)
    confirm_new_password = CharField(required=True)
