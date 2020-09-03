import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from blog.models import BlogPost
from blog.utils import is_image_aspect_ratio_valid, is_image_size_valid

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2
MIN_TITLE_LENGTH = 5
MIN_BODY_LENGTH = 20


class BlogPostSerializer(ModelSerializer):
    author = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "body", "image",
            "author", "slug", "date_published"
        ]

    def get_author(self, obj):
        return obj.author.username

    def get_image(self, obj):
        image = obj.image
        new_url = image.url
        if "?" in new_url:
            new_url = image.url[:image.url.rfind("?")]
        return new_url


class BlogPostUpdateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "image"]

    def validate(self, blog_post):
        try:
            title = blog_post['title']
            body = blog_post['body']
            image = blog_post['image']

            if len(title) < MIN_TITLE_LENGTH:
                raise ValidationError({
                    "response": "Enter a title longer than " + str(MIN_TITLE_LENGTH) + " characters",
                })

            if len(body) < MIN_BODY_LENGTH:
                raise ValidationError({
                    "response": "Enter a body longer than " + str(MIN_BODY_LENGTH) + " characters",
                })

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
        except KeyError:
            pass
        return blog_post


class BlogPostCreateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "image", "author", "date_updated"]

    def save(self):

        try:
            title = self.validated_data['title']
            body = self.validated_data['body']
            image = self.validated_data['image']

            if len(title) < MIN_TITLE_LENGTH:
                raise ValidationError({
                    "response": "Enter a title longer than " + str(MIN_TITLE_LENGTH) + " characters",
                })

            if len(body) < MIN_BODY_LENGTH:
                raise ValidationError({
                    "response": "Enter a body longer than " + str(MIN_BODY_LENGTH) + " characters",
                })

            blog_post = BlogPost(
                author=self.validated_data['author'],
                title=title,
                body=body,
                image=image,
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
                "response": "You must have title, body and image."
            })
