import os
import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from blog.utils import get_random_alphanumeric_string


def upload_location(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    rand_str = uuid.uuid4()

    filepath = 'uploads/{post_id}/{random_string}{ext}'.format(
        post_id=str(instance.post.id), random_string=rand_str, ext=file_extension
    )
    return filepath


class BlogPost(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        auto_created=True,
        verbose_name=_("ID"),
    )
    title = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("About")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Author")
    )
    slug = models.SlugField(
        max_length=100,
        blank=True,
        unique=True,
        verbose_name=_("Slug")
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name=_("blog_post_likes"),
        blank=True,
        verbose_name=_("Likes")
    )
    is_draft = models.BooleanField(
        default=False,
        verbose_name=_("Draft Status")
    )
    date_published = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Published")
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Updated")
    )

    class Meta:
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")

    def __str__(self):
        return str(self.id)


class PostImage(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        auto_created=True,
        verbose_name=_("ID"),
    )
    image = models.ImageField(
        upload_to=upload_location,
        null=True,
        blank=True,
        verbose_name=_("Image")
    )
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        verbose_name=_("Post")
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Added")
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Updated")
    )

    class Meta:
        verbose_name = _("Post Image")
        verbose_name_plural = _("Post Images")

    def __str__(self):
        return str(self.id)


@receiver(post_delete, sender=PostImage)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        rand_str = get_random_alphanumeric_string(16)
        instance.slug = slugify(str(instance.title) + "-" + rand_str)


pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)
