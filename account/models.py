import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        auto_created=True,
        verbose_name=_("ID"),
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("First Name"),
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Last Name"),
    )
    email = models.EmailField(
        max_length=60,
        unique=True,
        verbose_name=_("Email"),
    )
    username = models.CharField(
        max_length=30,
        unique=True
    )
    dob = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date of Birth"),
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Joined"),
    )
    last_login = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Login"),
    )
    is_valid = models.BooleanField(
        default=False,
        verbose_name=_("Is Verified"),
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name=_("Is Admin"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Is Staff"),
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_("Is Superuser"),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("All Users")

    # For checking permissions. to keep it simple all admin have ALL permissions
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)

    return 'profile_pictures/{user_id}/{random_string}{ext}'.format(
        user_id=instance.user.id, random_string=instance.id, ext=file_extension
    )


class ProfilePicture(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        auto_created=True,
        verbose_name=_("ID"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("User")
    )

    image = models.ImageField(
        upload_to=image_path,
        null=True,
        blank=True,
        verbose_name=_('Picture'),
    )

    uploaded_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Upload Time'),
    )

    class Meta:
        verbose_name = _("Profile Picture")
        verbose_name_plural = _("Profile Pictures")

    def __str__(self):
        return self.image.name
