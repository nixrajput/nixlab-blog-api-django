from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    Serializer,
    SerializerMethodField,
)

from account.models import Account, ProfilePicture


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
    image = SerializerMethodField()

    class Meta:
        model = ProfilePicture
        fields = "__all__"

    def get_image(self, obj):
        image = obj.image
        new_url = image.url
        if "?" in new_url:
            new_url = image.url[:image.url.rfind("?")]
        return new_url


class AccountDetailSerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id', 'first_name', 'last_name', 'image',
            'username', 'email', 'dob', 'phone',
        ]

    def get_image(self, obj):
        print(obj.id)
        image = ProfilePicture.objects.filter(user=obj.id).order_by('-uploaded_at')[0]

        serializer = ProfilePictureSerializer(image)

        return serializer.data


class AccountPropertiesSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'username', ]


class ChangePasswordSerializer(Serializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)
    confirm_new_password = CharField(required=True)
