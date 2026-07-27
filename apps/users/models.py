from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import Language, TimeStampedModel


class TelegramUser(TimeStampedModel):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=64, blank=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.RU)
    timezone = models.CharField(max_length=64, default="Asia/Tashkent")
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["telegram_id"]

    def __str__(self):
        return f"{self.telegram_id} (@{self.username or '—'})"

    def clean(self):
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValidationError({"timezone": "Unknown IANA timezone"}) from exc


class NotificationPreference(TimeStampedModel):
    user = models.OneToOneField(
        TelegramUser, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    enabled = models.BooleanField(default=True)
    random_messages_per_day = models.PositiveSmallIntegerField(default=2)
    random_window_start = models.TimeField(default=time(9, 0))
    random_window_end = models.TimeField(default=time(21, 0))
    schedule_version = models.PositiveIntegerField(default=0, editable=False)
    quiet_start = models.TimeField(default=time(22, 0))
    quiet_end = models.TimeField(default=time(7, 0))
    weekly_report_enabled = models.BooleanField(default=True)
    weekly_report_weekday = models.PositiveSmallIntegerField(
        default=6, help_text="0=Monday, 6=Sunday"
    )
    weekly_report_time = models.TimeField(default=time(20, 0))

    def clean(self):
        if self.random_messages_per_day > 10:
            raise ValidationError({"random_messages_per_day": "Maximum is 10"})
        if self.random_window_start >= self.random_window_end:
            raise ValidationError("Random notification start must be before end")
        start_minutes = self.random_window_start.hour * 60 + self.random_window_start.minute
        end_minutes = self.random_window_end.hour * 60 + self.random_window_end.minute
        available_slots = (end_minutes - start_minutes) // 30
        if self.random_messages_per_day > available_slots:
            raise ValidationError(
                {"random_messages_per_day": "Not enough half-hour slots in the window"}
            )
        if self.weekly_report_weekday > 6:
            raise ValidationError({"weekly_report_weekday": "Must be between 0 and 6"})

    def __str__(self):
        return f"Notifications for {self.user}"
