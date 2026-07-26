from django.db import models

from apps.core.models import Language, TimeStampedModel
from apps.users.models import TelegramUser


class EventType(models.TextChoices):
    MAJOR = "major", "Major date"
    VIRTUOUS = "virtuous", "Virtuous day"
    MONTH = "month", "Month"
    OTHER = "other", "Other"


class IslamicEvent(TimeStampedModel):
    slug = models.SlugField(unique=True)
    hijri_month = models.PositiveSmallIntegerField()
    hijri_day = models.PositiveSmallIntegerField()
    event_type = models.CharField(max_length=12, choices=EventType.choices, default=EventType.OTHER)
    requires_local_confirmation = models.BooleanField(default=True)
    reminder_days = models.JSONField(default=list, help_text="Days before the estimated occurrence")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["hijri_month", "hijri_day"]

    def __str__(self):
        return f"{self.hijri_day}/{self.hijri_month}: {self.slug}"


class EventTranslation(TimeStampedModel):
    event = models.ForeignKey(IslamicEvent, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "language"], name="unique_event_language")
        ]


class EventSubscription(TimeStampedModel):
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="event_subscriptions"
    )
    event = models.ForeignKey(IslamicEvent, on_delete=models.CASCADE, related_name="subscriptions")
    enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "event"], name="unique_event_subscription")
        ]


class CalendarCorrection(TimeStampedModel):
    event = models.ForeignKey(IslamicEvent, on_delete=models.CASCADE, related_name="corrections")
    hijri_year = models.PositiveIntegerField()
    region = models.CharField(max_length=100, default="global")
    gregorian_date = models.DateField()
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "hijri_year", "region"], name="unique_calendar_correction"
            )
        ]
