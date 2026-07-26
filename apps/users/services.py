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

    if settings.PERSONAL_BOT_MODE:
        if configured_owner and telegram_id != configured_owner:
            raise PersonalBotAccessDenied
        owner = TelegramUser.objects.select_for_update().filter(is_owner=True).first()
        if owner and owner.telegram_id != telegram_id:
            raise PersonalBotAccessDenied

    defaults = {
        "username": telegram_user.username or "",
        "first_name": telegram_user.first_name or "",
        "last_name": telegram_user.last_name or "",
        "last_seen_at": timezone.now(),
    }
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
