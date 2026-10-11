from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.core.models import Language

from .models import NotificationPreference, TelegramUser


class PersonalBotAccessDenied(Exception):
    pass


def normalize_language(language_code: str | None) -> str:
    base = (language_code or "ru").split("-")[0].lower()
    return base if base in Language.values else Language.RU


@transaction.atomic
def register_or_update_telegram_user(telegram_user) -> TelegramUser:
    telegram_id = int(telegram_user.id)
    configured_owner = settings.BOT_OWNER_TELEGRAM_ID
    existing = TelegramUser.objects.filter(telegram_id=telegram_id).first()
    if existing and not existing.is_active:
        raise PersonalBotAccessDenied

    if settings.PERSONAL_BOT_MODE:
        if configured_owner and telegram_id != configured_owner:
            raise PersonalBotAccessDenied
        owner = (
            TelegramUser.objects.select_for_update()
            .filter(is_owner=True, telegram_id__isnull=False)
            .first()
        )
        if owner and owner.telegram_id != telegram_id:
            raise PersonalBotAccessDenied

    defaults = {
        "username": telegram_user.username or "",
        "first_name": telegram_user.first_name or "",
        "last_name": telegram_user.last_name or "",
        "last_seen_at": timezone.now(),
    }
    if existing and existing.first_name_customized:
        defaults.pop("first_name")
    if existing:
        for field, value in defaults.items():
            setattr(existing, field, value)
        existing.save(update_fields=[*defaults, "updated_at"])
        user = existing
    else:
        user = TelegramUser.objects.create(
            telegram_id=telegram_id,
            language=normalize_language(telegram_user.language_code),
            is_owner=settings.PERSONAL_BOT_MODE,
            **defaults,
        )
    NotificationPreference.objects.get_or_create(user=user)
    if not existing:
        user_id = user.id

        def create_first_schedule():
            from apps.notifications.services import (
                plan_daily_for_user,
                plan_event_reminders_for_user,
                plan_weekly_report_for_user,
            )

            scheduled_user = TelegramUser.objects.select_related("notification_preferences").get(
                id=user_id
            )
            plan_daily_for_user(scheduled_user)
            plan_event_reminders_for_user(scheduled_user)
            plan_weekly_report_for_user(scheduled_user)

        transaction.on_commit(create_first_schedule)
    return user


def set_language(user: TelegramUser, language: str) -> TelegramUser:
    user.language = normalize_language(language)
    user.save(update_fields=["language", "updated_at"])
    return user


def _shift_half_hour(value, delta):
    base = datetime.combine(timezone.localdate(), value)
    return (base + timedelta(minutes=30 * delta)).time().replace(second=0, microsecond=0)


@transaction.atomic
def update_notification_preference(user: TelegramUser, action: str) -> NotificationPreference:
    preference = NotificationPreference.objects.select_for_update().get(user=user)
    previous = (
        preference.enabled,
        preference.random_messages_per_day,
        preference.random_window_start,
        preference.random_window_end,
        preference.weekly_report_enabled,
    )
    if action == "toggle":
        preference.enabled = not preference.enabled
    elif action == "count_down":
        preference.random_messages_per_day = max(0, preference.random_messages_per_day - 1)
    elif action == "count_up":
        preference.random_messages_per_day = min(10, preference.random_messages_per_day + 1)
    elif action == "start_down":
        candidate = _shift_half_hour(preference.random_window_start, -1)
        if candidate < preference.random_window_start:
            preference.random_window_start = candidate
    elif action == "start_up":
        candidate = _shift_half_hour(preference.random_window_start, 1)
        if candidate < preference.random_window_end:
            preference.random_window_start = candidate
    elif action == "end_down":
        candidate = _shift_half_hour(preference.random_window_end, -1)
        if candidate > preference.random_window_start:
            preference.random_window_end = candidate
    elif action == "end_up":
        candidate = _shift_half_hour(preference.random_window_end, 1)
        if candidate > preference.random_window_end:
            preference.random_window_end = candidate
    elif action == "weekly_toggle":
        preference.weekly_report_enabled = not preference.weekly_report_enabled
    else:
        raise ValueError("Unknown notification setting")
    current = (
        preference.enabled,
        preference.random_messages_per_day,
        preference.random_window_start,
        preference.random_window_end,
        preference.weekly_report_enabled,
    )
    if current == previous:
        raise ValueError("Notification setting is already at its limit")
    preference.schedule_version += 1
    preference.full_clean()
    preference.save()

    def replan():
        from apps.notifications.services import (
            replan_daily_for_user,
            replan_weekly_for_user,
        )

        refreshed = TelegramUser.objects.select_related("notification_preferences").get(id=user.id)
        replan_daily_for_user(refreshed)
        if action == "weekly_toggle":
            replan_weekly_for_user(refreshed)

    transaction.on_commit(replan)
    return preference


@transaction.atomic
def update_platform_settings(user, changes):
    """Validate all form fields together, then replan after the short write transaction."""
    user = TelegramUser.objects.select_for_update().get(id=user.id)
    preference, _ = NotificationPreference.objects.get_or_create(user=user)
    changed = False
    timezone_changed = False
    for field in ("language", "timezone"):
        if field in changes and getattr(user, field) != changes[field]:
            setattr(user, field, changes[field])
            timezone_changed |= field == "timezone"
            changed = True
    for field, value in changes.items():
        if field not in ("language", "timezone") and getattr(preference, field) != value:
            setattr(preference, field, value)
            changed = True
    user.full_clean()
    preference.full_clean()
    if not changed:
        return user, preference
    user.save(update_fields=["language", "timezone", "updated_at"])
    preference.schedule_version += 1
    preference.save()

    def replan():
        from apps.notifications.models import (
            NotificationKind,
            NotificationStatus,
            ScheduledNotification,
        )
        from apps.notifications.services import (
            plan_event_reminders_for_user,
            replan_daily_for_user,
            replan_weekly_for_user,
        )

        refreshed = TelegramUser.objects.select_related("notification_preferences").get(id=user.id)
        if timezone_changed:
            ScheduledNotification.objects.filter(
                user=refreshed,
                dedupe_key__startswith=f"daily:{refreshed.id}:",
                status=NotificationStatus.PENDING,
            ).update(status=NotificationStatus.SKIPPED)
        replan_daily_for_user(refreshed)
        replan_weekly_for_user(refreshed)
        if timezone_changed:
            ScheduledNotification.objects.filter(
                user=refreshed, kind=NotificationKind.EVENT, status=NotificationStatus.PENDING
            ).update(status=NotificationStatus.SKIPPED)
            plan_event_reminders_for_user(refreshed)

    transaction.on_commit(replan)
    return user, preference
