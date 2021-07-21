from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from account.models import ProfilePicture
from account.serializers import ProfilePictureSerializer
from blog.models import BlogPost

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2
DOES_NOT_EXIST = "DOES_NOT_EXIST"


class BlogPostSerializer(ModelSerializer):
    author_name = SerializerMethodField()
    author_username = SerializerMethodField()
    author_id = SerializerMethodField()
    token = SerializerMethodField()
    like_count = SerializerMethodField()
    is_liked = SerializerMethodField()
    profile_pic_url = SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "body", "image", "slug", "likes", "like_count", "date_published",
            "is_liked", "author_name", "author_username", "author_id", "profile_pic_url"
        ]

    def get_author_name(self, obj):
        return obj.author.first_name + " " + obj.author.last_name

    def get_author_username(self, obj):
        return obj.author.username

    def get_author_id(self, obj):
        return obj.author.id

    def get_profile_pic_url(self, obj):
        try:
            image = ProfilePicture.objects.filter(user=obj.author.id).order_by('-uploaded_at')[0]
        except (ProfilePicture.DoesNotExist, IndexError):
            image = ""

        serializer = ProfilePictureSerializer(image)

        return serializer.data

    # def get_token(self, obj):
    #
    #     try:
    #         token, _ = Token.objects.get_or_create(user=obj.author)
    #     except Token.DoesNotExist:
    #         raise ValidationError(DOES_NOT_EXIST)
    #
    #     is_expired, token = token_expire_handler(token)
    #
    #     return token.key

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        if self.context['request'].user in obj.likes.all():
            return True
        return False


class BlogPostUpdateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "image", "timestamp"]

    # def validate(self, blog_post):
    #     try:
    #         image = blog_post['image']
    #
    #         url = os.path.join(settings.TEMP, str(image))
    #         storage = FileSystemStorage(location=url)
    #
    #         with storage.open('', 'wb+') as destination:
    #             for chunk in image.chunks():
    #                 destination.write(chunk)
    #             destination.close()
    #
    #         if not is_image_size_valid(url, IMAGE_SIZE_MAX_BYTES):
    #             os.remove(url)
    #             raise ValidationError({
    #                 "response": "The image is too large. Image must be less than 2 MB."
    #             })
    #
    #         if not is_image_aspect_ratio_valid(url):
    #             os.remove(url)
    #             raise ValidationError({
    #                 "detail": "Image must be in square pixels."
    #             })
    #
    #         os.remove(url)
    #     except (KeyError, ValueError):
    #         raise ValidationError({
    #             "response": "An error occurred."
    #         })
    #     return blog_post


class BlogPostCreateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "image", "author"]

    def validate(self, data):
        if not data.get('image'):
            raise ValidationError({'image': 'This field is required.'})
        if not data.get('author'):
            raise ValidationError({'author': 'This field is required.'})

    def save(self):
        author = self.validated_data['author']
        title = self.validated_data['title']
        body = self.validated_data['body']
        image = self.validated_data['image']

        blog_post = BlogPost(
            author=author,
            title=title,
            body=body,
            image=image
        )

        blog_post.save()
        return blog_post
