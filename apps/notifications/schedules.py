from datetime import timedelta

from django.utils import timezone
from django_q.models import Schedule


def ensure_schedules():
    daily, _ = Schedule.objects.update_or_create(
        name="Plan personal daily notifications",
        defaults={
            "func": "apps.notifications.tasks.plan_daily_notifications",
            "schedule_type": Schedule.DAILY,
            "repeats": -1,
            "next_run": timezone.now() + timedelta(seconds=10),
        },
    )
    dispatcher, _ = Schedule.objects.update_or_create(
        name="Dispatch due Telegram notifications",
        defaults={
            "func": "apps.notifications.tasks.dispatch_due_notifications",
            "schedule_type": Schedule.MINUTES,
            "minutes": 1,
            "repeats": -1,
            "next_run": timezone.now() + timedelta(seconds=15),
        },
    )
    return daily, dispatcher
