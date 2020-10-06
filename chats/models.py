import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Chats(models.Model):
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
        verbose_name=_("UserID")
    )

    sender = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name=_("SenderID")
    )

    message = models.CharField(
        max_length=2000,
        null=True,
        blank=True,
        verbose_name=_("Text")
    )

    timestamp = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name=_("Timestamp")
    )

    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Sent Time")
    )

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

    def __str__(self):
        return str(self.user.id)
