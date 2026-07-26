import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.db import models
from django.utils import timezone

from apps.islamic_calendar.services import upcoming_events
from apps.learning.models import QuizAttempt, UserNameProgress
from apps.worship.models import WorshipEntry, WorshipKind
from apps.worship.services import balances_for_user

from .models import NotificationKind, ScheduledNotification, WeeklyReport


def _random_local_datetime(day, start, end, tz):
    start_dt = datetime.combine(day, start, tzinfo=tz)
    end_dt = datetime.combine(day, end, tzinfo=tz)
    seconds = max(0, int((end_dt - start_dt).total_seconds()))
    return start_dt + timedelta(seconds=random.randint(0, seconds))


def plan_daily_for_user(user, local_day=None):
    preferences = user.notification_preferences
    if not preferences.enabled or preferences.random_messages_per_day == 0:
        return []
    tz = ZoneInfo(user.timezone)
    local_day = local_day or timezone.now().astimezone(tz).date()
    kinds = [NotificationKind.QURAN, NotificationKind.DUA]
    if UserNameProgress.objects.filter(user=user).exists():
        kinds.append(NotificationKind.REVIEW)
    balances = balances_for_user(user)
    if balances["fast"] or any(balances["prayers"].values()):
        kinds.append(NotificationKind.QADA)
    created = []
    for index in range(preferences.random_messages_per_day):
        due_at = _random_local_datetime(
            local_day, preferences.random_window_start, preferences.random_window_end, tz
        )
        notification, was_created = ScheduledNotification.objects.get_or_create(
            dedupe_key=f"daily:{user.id}:{local_day.isoformat()}:{index}",
            defaults={"user": user, "kind": random.choice(kinds), "due_at": due_at},
        )
        if was_created:
            created.append(notification)
    return created


def plan_event_reminders_for_user(user, local_day=None):
    tz = ZoneInfo(user.timezone)
    local_day = local_day or timezone.now().astimezone(tz).date()
    created = []
    for occurrence in upcoming_events(user.language, from_date=local_day, days=14):
        days_until = (occurrence.date - local_day).days
        if days_until not in [*occurrence.event.reminder_days, 0]:
            continue
        if occurrence.event.subscriptions.filter(user=user, enabled=False).exists():
            continue
        due_at = datetime.combine(local_day, datetime.min.time().replace(hour=9), tzinfo=tz)
        notification, was_created = ScheduledNotification.objects.get_or_create(
            dedupe_key=f"event:{user.id}:{occurrence.event.id}:{occurrence.date}:{days_until}",
            defaults={
                "user": user,
                "kind": NotificationKind.EVENT,
                "due_at": due_at,
                "payload": {
                    "event_id": occurrence.event.id,
                    "occurrence_date": occurrence.date.isoformat(),
                    "days_until": days_until,
                    "estimated": occurrence.is_estimated,
                },
            },
        )
        if was_created:
            created.append(notification)
    return created


def build_weekly_report(user, period_end=None):
    tz = ZoneInfo(user.timezone)
    period_end = period_end or timezone.now().astimezone(tz).date()
    period_start = period_end - timedelta(days=6)
    start_dt = datetime.combine(period_start, datetime.min.time(), tzinfo=tz)
    end_dt = datetime.combine(period_end + timedelta(days=1), datetime.min.time(), tzinfo=tz)
    attempts = QuizAttempt.objects.filter(
        user=user, created_at__gte=start_dt, created_at__lt=end_dt
    )
    total = attempts.count()
    correct = attempts.filter(is_correct=True).count()
    introduced = UserNameProgress.objects.filter(
        user=user, introduced_at__gte=start_dt, introduced_at__lt=end_dt
    ).count()
    learned = UserNameProgress.objects.filter(user=user, status="learned").count()
    prayer_completed = abs(
        WorshipEntry.objects.filter(
            user=user,
            kind=WorshipKind.PRAYER,
            amount__lt=0,
            created_at__gte=start_dt,
            created_at__lt=end_dt,
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )
    fast_completed = abs(
        WorshipEntry.objects.filter(
            user=user,
            kind=WorshipKind.FAST,
            amount__lt=0,
            created_at__gte=start_dt,
            created_at__lt=end_dt,
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )
    favorites_added = user.favorites.filter(created_at__gte=start_dt, created_at__lt=end_dt).count()
    data = {
        "introduced": introduced,
        "learned_total": learned,
        "reviews": total,
        "correct": correct,
        "accuracy": round(correct * 100 / total) if total else 0,
        "prayer_completed": prayer_completed,
        "fast_completed": fast_completed,
        "favorites_added": favorites_added,
    }
    from apps.telegram_bot.i18n import render_weekly_report

    text = render_weekly_report(user.language, period_start, period_end, data)
    report, _ = WeeklyReport.objects.update_or_create(
        user=user,
        period_start=period_start,
        period_end=period_end,
        defaults={"language": user.language, "data": data, "rendered_text": text},
    )
    return report


def plan_weekly_report_for_user(user, local_day=None):
    preferences = user.notification_preferences
    if not preferences.weekly_report_enabled:
        return None
    tz = ZoneInfo(user.timezone)
    local_day = local_day or timezone.now().astimezone(tz).date()
    if local_day.weekday() != preferences.weekly_report_weekday:
        return None
    due_at = datetime.combine(local_day, preferences.weekly_report_time, tzinfo=tz)
    notification, _ = ScheduledNotification.objects.get_or_create(
        dedupe_key=f"weekly:{user.id}:{local_day.isoformat()}",
        defaults={"user": user, "kind": NotificationKind.WEEKLY_REPORT, "due_at": due_at},
    )
    return notification
