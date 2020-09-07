import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from blog.models import BlogPost
from blog.utils import is_image_aspect_ratio_valid, is_image_size_valid

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2
DOES_NOT_EXIST = "DOES_NOT_EXIST"


class BlogPostSerializer(ModelSerializer):
    author = SerializerMethodField()
    author_id = SerializerMethodField()
    token = SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "body", "image", "slug",
            "author", "author_id", "token",  "timestamp"
        ]

    def get_author(self, obj):
        return obj.author.username

    def get_author_id(self, obj):
        return obj.author.id

    def get_token(self, obj):
        try:
            token = Token.objects.get(user=obj.author)
        except Token.DoesNotExist:
            raise ValidationError(DOES_NOT_EXIST)
        return token.key


class BlogPostUpdateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "image", "timestamp"]

    def validate(self, blog_post):
        try:
            image = blog_post['image']

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
        except (KeyError, ValueError):
            raise ValidationError({
                "response": "An error occurred."
            })
        return blog_post


class BlogPostCreateSerializer(ModelSerializer):

    class Meta:
        model = BlogPost
        fields = ["title", "body", "image", "author", "timestamp"]

    def save(self):

        try:
            title = self.validated_data['title']
            body = self.validated_data['body']
            image = self.validated_data['image']
            timestamp = self.validated_data['timestamp']

            blog_post = BlogPost(
                author=self.validated_data['author'],
                title=title,
                body=body,
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
            blog_post.save()
            return blog_post
        except KeyError:
            raise ValidationError({
                "response": "You must have all the fields not null."
            })
