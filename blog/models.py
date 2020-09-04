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

    filepath = 'uploads/{author_id}/{random_string}{ext}'.format(
        author_id=str(instance.author.id), random_string=rand_str, ext=file_extension
    )
    return filepath


class BlogPost(models.Model):
    title = models.CharField(
        max_length=100,
        null=False,
        blank=True,
        verbose_name=_("Title")
    )
    body = models.CharField(
        max_length=500,
        null=False,
        blank=True,
        verbose_name=_("Body")
    )
    image = models.ImageField(
        upload_to=upload_location,
        null=True,
        blank=True,
        verbose_name=_("Image")
    )
    date_published = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Published"
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Date Updated"
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

    class Meta:
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")

    def __str__(self):
        return self.title


@receiver(post_delete, sender=BlogPost)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        rand_str1 = get_random_alphanumeric_string(8)
        rand_str2 = get_random_alphanumeric_string(8)
        instance.slug = slugify(rand_str1 + "-" + instance.title + "-" + rand_str2)


pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)
