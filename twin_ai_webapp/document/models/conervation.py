import uuid

from django.db import models


class Conversation(models.Model):
    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        db_table = "conversations"
        ordering = ["-created_at"]

    uuid = models.UUIDField(
        editable=False,
        unique=True,
        default=uuid.uuid4,
    )
    user = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    user_message = models.TextField(
        null=True,
        blank=True,
    )
    assistant_message = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
