from django.contrib import admin

from .models import AudioAsset, AudioBinding


@admin.register(AudioAsset)
class AudioAssetAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "voice",
        "provider",
        "is_published",
        "available",
        "rights_confirmed",
        "pronunciation_verified",
        "expires_at",
    )
    list_filter = ("provider", "is_published", "available", "rights_confirmed")
    search_fields = ("key", "voice")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(AudioBinding)
class AudioBindingAdmin(admin.ModelAdmin):
    list_display = ("asset", "name", "passage", "dua", "arabic_item", "verse", "word", "order")
