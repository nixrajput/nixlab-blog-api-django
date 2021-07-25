import secrets
from datetime import datetime, date

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
        fields = ["first_name", "last_name", "email", "username", "password", "password2"]
        extra_kwargs = {"password2": {"write_only": True}}

    def validate(self, data):
        if not data.get('first_name'):
            raise ValidationError({'first_name': 'This field is required.'})
        if not data.get('last_name'):
            raise ValidationError({'last_name': 'This field is required.'})
        if not data.get('email'):
            raise ValidationError({'email': 'This field is required.'})
        if not data.get('username'):
            raise ValidationError({'username': 'This field is required.'})
        if not data.get('password'):
            raise ValidationError({'password': 'This field is required.'})
        if not data.get('password2'):
            raise ValidationError({'password2': 'This field is required.'})

        return data

    def save(self, **kwargs):

        first_name = self.validated_data["first_name"]
        last_name = self.validated_data["last_name"]
        email = self.validated_data["email"]
        username = self.validated_data["username"]
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        account = Account(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            about="Hello there, I am {f_name} {l_name}.".format(f_name=first_name, l_name=last_name)
        )

        if not secrets.compare_digest(password, password2):
            raise ValidationError({
                'response': 'error',
                "message": "Password doesn't matched."
            })
        account.set_password(password)
        account.save()
        return account


class LoginSerializer(Serializer):
    username = CharField(required=True)
    password = CharField(required=True)


class ProfilePictureSerializer(ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ["id", "image", "user"]


class ProfilePictureUploadSerializer(ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ['user', 'image']

    def validate(self, data):
        if not data.get('image'):
            raise ValidationError({'image': 'This field is required.'})
        return data

    def save(self):
        image = self.validated_data['image']

        profile_pic = ProfilePicture(
            user=self.validated_data['user'],
            image=image
        )

        profile_pic.save()
        return profile_pic


class AccountDetailSerializer(ModelSerializer):
    img_url = SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'username', 'email',
            'about', 'dob', 'gender', "followers", "following", 'img_url',
            'is_valid', 'account_type', 'date_joined', 'last_login'
        ]

    def get_img_url(self, obj):
        try:
            image = ProfilePicture.objects.filter(user=obj.id).order_by('-uploaded_at')[0]
        except (ProfilePicture.DoesNotExist, IndexError):
            image = ""

        serializer = ProfilePictureSerializer(image)

        return serializer.data["image"]


class AccountPropertiesSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "first_name", "last_name", "phone",
            "dob", 'gender', "about"
        ]

    def validate(self, data):
        if not data.get('first_name'):
            raise ValidationError({'first_name': 'This field is required.'})
        if not data.get('last_name'):
            raise ValidationError({'last_name': 'This field is required.'})
        if data.get('phone') and len(data.get('phone')) < 10:
            raise ValidationError({'email': 'Phone number is invalid.'})
        if data.get('dob'):
            birthDate = datetime.strptime(str(data["dob"]), "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birthDate.year - ((today.month, today.day) <
                                                 (birthDate.month, birthDate.day))
            if age < 6:
                raise ValidationError({"dob": 'You must be older than 6 years old.'})
            data["dob"] = birthDate

        if data.get('about'):
            data["about"] = data["about"]
        else:
            data["about"] = None

        return data


class ChangePasswordSerializer(Serializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)
    confirm_new_password = CharField(required=True)
