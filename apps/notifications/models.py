from django.db import models

from apps.core.models import TimeStampedModel
from apps.users.models import TelegramUser


class NotificationKind(models.TextChoices):
    REVIEW = "review", "Learning review"
    QURAN = "quran", "Quran passage"
    DUA = "dua", "Dua"
    QADA = "qada", "Qada reminder"
    EVENT = "event", "Islamic event"
    WEEKLY_REPORT = "weekly_report", "Weekly report"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    SKIPPED = "skipped", "Skipped"


class ScheduledNotification(TimeStampedModel):
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="scheduled_notifications"
    )
    kind = models.CharField(max_length=20, choices=NotificationKind.choices)
    due_at = models.DateTimeField(db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=150, unique=True)
    status = models.CharField(
        max_length=12,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ["due_at"]


class WeeklyReport(TimeStampedModel):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="weekly_reports")
    period_start = models.DateField()
    period_end = models.DateField()
    language = models.CharField(max_length=2)
    data = models.JSONField(default=dict)
    rendered_text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "period_start", "period_end"], name="unique_weekly_report_period"
            )
        ]
        ordering = ["-period_end"]
