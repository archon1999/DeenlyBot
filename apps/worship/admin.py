from django.contrib import admin

from .models import QadaPrayer, QadaProfile, WorshipEntry


@admin.register(WorshipEntry)
class WorshipEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "prayer_type", "amount", "occurred_on", "note")
    list_filter = ("kind", "prayer_type", "occurred_on")


@admin.register(QadaProfile)
class QadaProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "historical_start_date",
        "historical_start_prayer",
        "historical_cursor_date",
        "historical_cursor_prayer",
        "historical_completed",
    )


@admin.register(QadaPrayer)
class QadaPrayerAdmin(admin.ModelAdmin):
    list_display = ("user", "prayer_date", "prayer_type", "source", "status", "completed_at")
    list_filter = ("source", "status", "prayer_type")
