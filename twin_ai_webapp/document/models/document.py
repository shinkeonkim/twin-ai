import uuid

from agent.utils.chroma_tool import (
    add_document_to_chroma,
    delete_document_from_chroma,
    update_document_in_chroma,
)
from django.db import models
from django.utils import timezone

from .obsidian_file import ObsidianFile


class Document(models.Model):
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        db_table = "documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["synced_at"]),
        ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.ForeignKey(
        "PdfFile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )
    obsidian_file = models.ForeignKey(
        ObsidianFile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )

    def save(self, *args, **kwargs):
        document_content = f"제목: {self.title}\n내용: {self.content}"
        if self.synced_at is None:
            add_document_to_chroma(str(self.uuid), document_content)
            self.synced_at = timezone.now()
        else:
            update_document_in_chroma(str(self.uuid), document_content)
            self.synced_at = timezone.now()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_document_from_chroma(str(self.uuid))
        super().delete(*args, **kwargs)
