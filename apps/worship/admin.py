from django.contrib import admin

from .models import WorshipEntry


@admin.register(WorshipEntry)
class WorshipEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "prayer_type", "amount", "occurred_on", "note")
    list_filter = ("kind", "prayer_type", "occurred_on")
