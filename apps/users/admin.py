from django.contrib import admin

from .models import NotificationPreference, TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "language",
        "timezone",
        "is_owner",
        "is_active",
        "last_seen_at",
    )
    list_filter = ("language", "is_owner", "is_active")
    search_fields = ("telegram_id", "username", "first_name", "last_name")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "enabled", "random_messages_per_day", "weekly_report_enabled")
