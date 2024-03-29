from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ListField,
    FileField
)

from account.models import ProfilePicture
from account.serializers import ProfilePictureSerializer
from blog.models import BlogPost, PostImage


class PostImageSerializer(ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "image", "post"]


class BlogPostSerializer(ModelSerializer):
    author_name = SerializerMethodField()
    author_username = SerializerMethodField()
    author_id = SerializerMethodField()
    author_img_url = SerializerMethodField()
    like_count = SerializerMethodField()
    is_liked = SerializerMethodField()
    image_urls = SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id", "content", "image_urls", "author_id", "author_name", "author_username",
            "author_img_url", "slug", "likes", "like_count", "is_liked", "date_published",
            "last_updated"
        ]

    @staticmethod
    def get_author_name(obj):
        return obj.author.first_name + " " + obj.author.last_name

    @staticmethod
    def get_author_username(obj):
        return obj.author.username

    @staticmethod
    def get_author_id(obj):
        return obj.author.id

    @staticmethod
    def get_image_urls(obj):
        try:
            post_images = PostImage.objects.filter(post=obj.id).order_by('date_added')
        except (PostImage.DoesNotExist, IndexError):
            post_images = None

        serializer = PostImageSerializer(post_images, many=True)

        return [data["image"] for data in serializer.data]

    @staticmethod
    def get_author_img_url(obj):
        try:
            image = ProfilePicture.objects.filter(user=obj.author.id).order_by('-uploaded_at')[0]
        except (ProfilePicture.DoesNotExist, IndexError):
            image = None

        serializer = ProfilePictureSerializer(image)

        return serializer.data["image"]

    @staticmethod
    def get_like_count(obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        if self.context['request'].user in obj.likes.all():
            return True
        return False


class BlogPostUpdateSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["content"]

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
    image_files = ListField(
        child=FileField(
            allow_empty_file=True,
            use_url=False,
        ),
        required=False
    )

    class Meta:
        model = BlogPost
        fields = ["content", "image_files", "author"]

    def validate(self, data):
        if not data.get('author'):
            raise ValidationError('Author field is required.')
        if not data.get('content'):
            data['content'] = None
        if not data.get('image_files'):
            data['image_files'] = []

        return data

    def save(self):
        author = self.validated_data['author']

        if self.validated_data['content'] is not None:
            content = self.validated_data['content']
        else:
            content = None

        blog_post = BlogPost(
            author=author,
            content=content
        )
        blog_post.save()

        if len(self.validated_data['image_files']) > 0:
            image_files = self.validated_data.pop('image_files')
            for img in image_files:
                PostImage.objects.create(post=blog_post, image=img)

        return blog_post
