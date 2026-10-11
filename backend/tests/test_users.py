from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.utils import timezone

from apps.notifications.models import NotificationKind, NotificationStatus, ScheduledNotification
from apps.notifications.services import plan_weekly_report_for_user
from apps.users.models import TelegramUser
from apps.users.services import (
    PersonalBotAccessDenied,
    register_or_update_telegram_user,
    update_notification_preference,
)


def telegram_user(identifier, language="en"):
    return SimpleNamespace(
        id=identifier,
        username=f"user{identifier}",
        first_name="Test",
        last_name="User",
        language_code=language,
    )


@pytest.mark.django_db
@override_settings(PERSONAL_BOT_MODE=True, BOT_OWNER_TELEGRAM_ID=None)
def test_first_user_becomes_owner_and_second_is_denied():
    first = register_or_update_telegram_user(telegram_user(10, "uz-UZ"))
    assert first.is_owner is True
    assert first.language == "uz"
    assert hasattr(first, "notification_preferences")

    with pytest.raises(PersonalBotAccessDenied):
        register_or_update_telegram_user(telegram_user(11))
    assert TelegramUser.objects.count() == 1


@pytest.mark.django_db
@override_settings(PERSONAL_BOT_MODE=True, BOT_OWNER_TELEGRAM_ID=55)
def test_configured_owner_is_enforced():
    with pytest.raises(PersonalBotAccessDenied):
        register_or_update_telegram_user(telegram_user(54))
    assert register_or_update_telegram_user(telegram_user(55)).telegram_id == 55


@pytest.mark.django_db
@override_settings(PERSONAL_BOT_MODE=True, BOT_OWNER_TELEGRAM_ID=None)
def test_new_owner_gets_a_schedule_immediately(django_capture_on_commit_callbacks):
    now = timezone.make_aware(datetime(2026, 7, 26, 8))
    with patch("apps.notifications.services.timezone.now", return_value=now):
        with django_capture_on_commit_callbacks(execute=True):
            register_or_update_telegram_user(telegram_user(77))
    assert (
        ScheduledNotification.objects.filter(
            user__telegram_id=77, dedupe_key__startswith="daily:"
        ).count()
        == 2
    )


@pytest.mark.django_db
def test_notification_settings_update_and_replan(user, django_capture_on_commit_callbacks):
    now = timezone.make_aware(datetime(2026, 7, 26, 8))
    with patch("apps.notifications.services.timezone.now", return_value=now):
        with django_capture_on_commit_callbacks(execute=True):
            preference = update_notification_preference(user, "count_up")

    assert preference.random_messages_per_day == 3
    assert preference.schedule_version == 1
    planned = ScheduledNotification.objects.filter(user=user, dedupe_key__contains=":v1:")
    assert planned.count() == 3
    assert {item.due_at.minute for item in planned} <= {0, 30}


@pytest.mark.django_db
def test_disabling_weekly_report_skips_pending_report(user, django_capture_on_commit_callbacks):
    report = ScheduledNotification.objects.create(
        user=user,
        kind=NotificationKind.WEEKLY_REPORT,
        due_at=timezone.now(),
        dedupe_key="weekly-settings-test",
    )
    with django_capture_on_commit_callbacks(execute=True):
        update_notification_preference(user, "weekly_toggle")
    report.refresh_from_db()
    assert report.status == NotificationStatus.SKIPPED


@pytest.mark.django_db
def test_reenabling_weekly_report_restores_the_same_day_schedule(
    user, django_capture_on_commit_callbacks
):
    now = timezone.make_aware(datetime(2026, 7, 26, 8))
    with patch("apps.notifications.services.timezone.now", return_value=now):
        report = plan_weekly_report_for_user(user)
        with django_capture_on_commit_callbacks(execute=True):
            update_notification_preference(user, "weekly_toggle")
        report.refresh_from_db()
        assert report.status == NotificationStatus.SKIPPED
        with django_capture_on_commit_callbacks(execute=True):
            update_notification_preference(user, "weekly_toggle")
    report.refresh_from_db()
    assert report.status == NotificationStatus.PENDING
    assert ScheduledNotification.objects.filter(kind=NotificationKind.WEEKLY_REPORT).count() == 1
