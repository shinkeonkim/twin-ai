import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from document.services.pdf_document_service import process_pdf_and_create_documents


class PdfFile(models.Model):
    class Meta:
        verbose_name = "PdfFile"
        verbose_name_plural = "PdfFiles"
        db_table = "pdf_files"
        ordering = ["-created_at"]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.FileField(
        upload_to="pdf_files/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            process_pdf_and_create_documents(self)
