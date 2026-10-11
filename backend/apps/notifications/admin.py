from django.contrib import admin

from .models import ScheduledNotification, WeeklyReport


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "due_at", "status", "attempts", "sent_at")
    list_filter = ("kind", "status")
    search_fields = ("dedupe_key", "last_error")


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("user", "period_start", "period_end", "language")
    readonly_fields = ("data", "rendered_text")
