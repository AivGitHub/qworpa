from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UUID4HEXNotGenerated(Exception):
    """UUID4 hex is not generated."""


def get_message_hex(tries=5):
    for _ in range(tries):
        uuid4_hex = uuid4().hex
        try:
            Message.objects.get(hex=uuid4_hex)
        except Message.DoesNotExist:
            return uuid4_hex
    else:
        raise UUID4HEXNotGenerated()


class Message(models.Model):
    hex = models.CharField(
        _("Message hex"),
        max_length=32,
        default=get_message_hex,
        editable=False,
        null=False,
        blank=False,
        unique=True
    )
    text = models.TextField(
        _("Message text"),
        editable=False,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(
        _("Created date"),
        default=timezone.now
    )
