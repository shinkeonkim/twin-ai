from django.contrib import admin

from .models import Conversation, Document, PdfFile


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "synced_at")
    list_filter = ("created_at", "synced_at")
    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at", "synced_at")
    fields = ("title", "content", "pdf_file", "synced_at")
    list_per_page = 20


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "user_message", "assistant_message", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user", "user_message", "assistant_message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fields = ("user", "user_message", "assistant_message")
    list_per_page = 20


@admin.register(PdfFile)
class PdfFileAdmin(admin.ModelAdmin):
    list_display = ("uuid", "file", "created_at")
    list_filter = ("created_at",)
    search_fields = ("file",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fields = ("file",)
    list_per_page = 20
