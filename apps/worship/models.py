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
