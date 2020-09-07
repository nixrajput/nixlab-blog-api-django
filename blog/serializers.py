import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from blog.models import BlogPost
from blog.utils import is_image_aspect_ratio_valid, is_image_size_valid

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2


class BlogPostSerializer(ModelSerializer):
    author = SerializerMethodField()
    image = SerializerMethodField()
    timestamp = SerializerMethodField()
    author_id = SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "body", "image",
            "author", "author_id", "slug", "timestamp"
        ]

    def get_author(self, obj):
        return obj.author.username

    def get_author_id(self, obj):
        return obj.author.id

    def get_image(self, obj):
        image = obj.image
        new_url = image.url
        if "?" in new_url:
            new_url = image.url[:image.url.rfind("?")]
        return new_url

    def get_timestamp(self, obj):
        date = obj.date_published
        format_date = date.strftime("%d %b, %Y")
        return format_date


class BlogPostUpdateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "image"]

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
    timestamp = SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ["title", "body", "image", "author", "timestamp"]

    def save(self):

        try:
            title = self.validated_data['title']
            body = self.validated_data['body']
            image = self.validated_data['image']

            # if len(title) < MIN_TITLE_LENGTH:
            #     raise ValidationError({
            #         "response": "Enter a title longer than " + str(MIN_TITLE_LENGTH) + " characters",
            #     })
            #
            # if len(body) < MIN_BODY_LENGTH:
            #     raise ValidationError({
            #         "response": "Enter a body longer than " + str(MIN_BODY_LENGTH) + " characters",
            #     })

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

    def get_timestamp(self, obj):
        date = obj.date_published
        format_date = date.strftime("%d %b, %Y")
        return format_date
