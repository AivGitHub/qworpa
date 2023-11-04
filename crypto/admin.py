from django.contrib import admin

from crypto.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "hex",
    )
    search_fields = (
        "hex",
        "text",
    )
    readonly_fields = (
        "hex",
        "text",
    )
