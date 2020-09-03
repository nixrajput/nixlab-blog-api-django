from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


def upload_location(instance, filename, **kwargs):
    filepath = 'uploads/{author_id}/{title}-{filename}'.format(
        author_id=str(instance.author.id), title=str(instance.title), filename=filename
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
        blank=True,
        unique=True,
        verbose_name=_("Slug")
    )

    def __str__(self):
        return self.title


@receiver(post_delete, sender=BlogPost)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)


pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)
