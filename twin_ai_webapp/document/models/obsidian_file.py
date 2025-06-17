from django.db import models


class ObsidianFile(models.Model):
    file_path = models.CharField(max_length=1024, unique=True)
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Obsidian File"
        verbose_name_plural = "Obsidian Files"
        db_table = "obsidian_files"

    def __str__(self):
        return self.file_path
