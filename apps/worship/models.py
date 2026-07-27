from django.db import models

from apps.core.models import TimeStampedModel
from apps.users.models import TelegramUser


class WorshipKind(models.TextChoices):
    PRAYER = "prayer", "Prayer"
    FAST = "fast", "Fast"


class PrayerType(models.TextChoices):
    FAJR = "fajr", "Fajr"
    DHUHR = "dhuhr", "Dhuhr"
    ASR = "asr", "Asr"
    MAGHRIB = "maghrib", "Maghrib"
    ISHA = "isha", "Isha"
    WITR = "witr", "Witr"


class QadaSource(models.TextChoices):
    MANUAL = "manual", "Missed after the starting date"
    HISTORICAL = "historical", "Historical debt"


class QadaStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"


class QadaProfile(TimeStampedModel):
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name="qada_profile")
    historical_start_date = models.DateField(null=True, blank=True)
    historical_start_prayer = models.CharField(
        max_length=10, choices=PrayerType.choices, blank=True
    )
    historical_cursor_date = models.DateField(null=True, blank=True)
    historical_cursor_prayer = models.CharField(
        max_length=10, choices=PrayerType.choices, blank=True
    )
    historical_completed = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    historical_start_prayer__in=["", "fajr", "dhuhr", "asr", "maghrib", "isha"]
                ),
                name="qada_profile_start_no_witr",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    historical_cursor_prayer__in=["", "fajr", "dhuhr", "asr", "maghrib", "isha"]
                ),
                name="qada_profile_cursor_no_witr",
            ),
        ]

    @property
    def historical_configured(self):
        return bool(self.historical_cursor_date and self.historical_cursor_prayer)

    def __str__(self):
        return f"Qada settings for {self.user}"


class QadaPrayer(TimeStampedModel):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="qada_prayers")
    source = models.CharField(max_length=12, choices=QadaSource.choices)
    prayer_date = models.DateField(db_index=True)
    prayer_type = models.CharField(max_length=10, choices=PrayerType.choices)
    status = models.CharField(
        max_length=12, choices=QadaStatus.choices, default=QadaStatus.PENDING, db_index=True
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "source", "prayer_date", "prayer_type"],
                name="unique_qada_prayer",
            ),
            models.CheckConstraint(
                condition=models.Q(prayer_type__in=["fajr", "dhuhr", "asr", "maghrib", "isha"]),
                name="qada_prayer_no_witr",
            ),
        ]
        ordering = ["-prayer_date", "-created_at"]

    def __str__(self):
        return f"{self.user}: {self.prayer_date} {self.prayer_type} ({self.source})"


class WorshipEntry(TimeStampedModel):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="worship_entries")
    kind = models.CharField(max_length=10, choices=WorshipKind.choices)
    prayer_type = models.CharField(max_length=10, choices=PrayerType.choices, blank=True)
    amount = models.IntegerField(help_text="Positive adds debt, negative records completion")
    occurred_on = models.DateField()
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-occurred_on", "-created_at"]

    def __str__(self):
        suffix = f"/{self.prayer_type}" if self.prayer_type else ""
        return f"{self.user}: {self.kind}{suffix} {self.amount:+d}"
