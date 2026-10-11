from datetime import date, time, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from django.core.management import call_command
from django.utils import timezone
from hijridate import Hijri

from apps.arabic_learning.models import ArabicLesson, ArabicQuizAttempt, ArabicQuizQuestion
from apps.arabic_learning.services import complete_lesson
from apps.islamic_calendar.models import EventTranslation, IslamicEvent
from apps.learning.models import QuizAttempt, QuizQuestion, QuizType
from apps.notifications.models import NotificationKind, ScheduledNotification
from apps.notifications.services import (
    build_weekly_report,
    plan_daily_for_user,
    plan_event_reminders_for_user,
    plan_weekly_report_for_user,
)
from apps.notifications.tasks import deliver_notification, dispatch_due_notifications
from apps.worship.models import PrayerType, WorshipKind
from apps.worship.services import add_debt, add_manual_qada, complete_one


@pytest.mark.django_db
def test_daily_plan_is_idempotent_and_in_user_window(user):
    preferences = user.notification_preferences
    preferences.random_messages_per_day = 3
    preferences.save()
    local_day = date(2030, 7, 26)
    first = plan_daily_for_user(user, local_day)
    second = plan_daily_for_user(user, local_day)
    assert len(first) == 3
    assert second == []
    assert ScheduledNotification.objects.count() == 3
    assert all(item.due_at.date() == local_day for item in first)


@pytest.mark.django_db
def test_qada_is_added_to_random_pool_only_when_debt_exists(user):
    add_manual_qada(user, date(2026, 7, 27), PrayerType.FAJR)
    user.notification_preferences.random_messages_per_day = 10
    user.notification_preferences.save()
    with patch("apps.notifications.services.random.choice", side_effect=lambda values: values[-1]):
        kinds = {item.kind for item in plan_daily_for_user(user, date(2030, 7, 27))}
    assert kinds == {NotificationKind.QADA}


@pytest.mark.django_db
def test_random_notifications_use_unique_half_hour_slots(user):
    preferences = user.notification_preferences
    preferences.random_messages_per_day = 10
    preferences.random_window_start = time(9, 10)
    preferences.random_window_end = time(14, 30)
    preferences.save()

    planned = plan_daily_for_user(user, date(2030, 7, 28))
    local_times = [item.due_at.time() for item in planned]

    assert len(local_times) == 10
    assert len(set(local_times)) == 10
    assert {value.minute for value in local_times} <= {0, 30}
    assert all(value.second == 0 and value.microsecond == 0 for value in local_times)


@pytest.mark.django_db
def test_replan_command_replaces_legacy_daily_schedule(user):
    local_day = timezone.localdate().isoformat()
    legacy_key = f"daily:{user.id}:{local_day}:0"
    ScheduledNotification.objects.create(
        user=user,
        kind=NotificationKind.DUA,
        due_at=timezone.now(),
        dedupe_key=legacy_key,
    )
    call_command("replan_random_notifications", verbosity=0)

    legacy = ScheduledNotification.objects.get(dedupe_key=legacy_key)
    assert legacy.status == "skipped"
    replanned = ScheduledNotification.objects.filter(user=user, dedupe_key__contains=":v1:")
    assert replanned.count() <= user.notification_preferences.random_messages_per_day
    assert all(item.due_at > timezone.now() for item in replanned)


@pytest.mark.django_db
def test_replanning_current_day_never_uses_past_slots(user):
    preferences = user.notification_preferences
    preferences.random_messages_per_day = 10
    preferences.random_window_start = time(9, 0)
    preferences.random_window_end = time(17, 0)
    preferences.save()
    now = timezone.make_aware(timezone.datetime(2026, 7, 27, 15, 10))

    with patch("apps.notifications.services.timezone.now", return_value=now):
        planned = plan_daily_for_user(user, date(2026, 7, 27))

    assert [item.due_at.time() for item in planned] == [
        time(15, 30),
        time(16, 0),
        time(16, 30),
    ]


@pytest.mark.django_db
def test_replanning_does_not_exceed_daily_count_after_messages_were_sent(user):
    local_day = date(2030, 7, 29)
    ScheduledNotification.objects.create(
        user=user,
        kind=NotificationKind.DUA,
        due_at=timezone.now(),
        dedupe_key=f"daily:{user.id}:{local_day.isoformat()}:legacy:0",
        status="sent",
    )

    planned = plan_daily_for_user(user, local_day)

    assert len(planned) == user.notification_preferences.random_messages_per_day - 1


@pytest.mark.django_db
def test_replanning_does_not_reuse_a_queued_half_hour_slot(user):
    preferences = user.notification_preferences
    preferences.random_messages_per_day = 3
    preferences.random_window_start = time(9)
    preferences.random_window_end = time(10, 30)
    preferences.save()
    local_day = date(2030, 7, 29)
    committed_time = timezone.make_aware(timezone.datetime(2030, 7, 29, 9))
    queued = ScheduledNotification.objects.create(
        user=user,
        kind=NotificationKind.DUA,
        due_at=committed_time,
        dedupe_key=f"daily:{user.id}:{local_day.isoformat()}:legacy:queued",
        status="queued",
    )

    planned = plan_daily_for_user(user, local_day)

    assert len(planned) == 2
    assert {item.due_at.time() for item in planned} == {time(9, 30), time(10)}
    queued.refresh_from_db()
    assert queued.status == "queued"


@pytest.mark.django_db
def test_arabic_review_is_added_to_daily_pool_after_completed_lesson(user):
    from django.core.management import call_command

    call_command("seed_arabic", verbosity=0)
    lesson = ArabicLesson.objects.get(category="alphabet", order=1)
    complete_lesson(user, lesson.id)
    user.notification_preferences.random_messages_per_day = 1
    user.notification_preferences.save()
    with patch(
        "apps.notifications.services.random.choice",
        side_effect=lambda values: (
            NotificationKind.ARABIC_REVIEW
            if NotificationKind.ARABIC_REVIEW in values
            else values[0]
        ),
    ):
        planned = plan_daily_for_user(user, date(2026, 7, 28))
    assert planned[0].kind == NotificationKind.ARABIC_REVIEW


@pytest.mark.django_db
def test_event_reminder_is_planned_once(user):
    today_hijri = Hijri.today()
    event = IslamicEvent.objects.create(
        slug="today-event",
        hijri_month=today_hijri.month,
        hijri_day=today_hijri.day,
        reminder_days=[0],
    )
    EventTranslation.objects.create(event=event, language="ru", title="Сегодня")
    local_day = date.today()
    first = plan_event_reminders_for_user(user, local_day)
    second = plan_event_reminders_for_user(user, local_day)
    assert len(first) == 1
    assert second == []
    assert first[0].payload["event_id"] == event.id


@pytest.mark.django_db
def test_due_dispatcher_claims_each_notification_once(user):
    notification = ScheduledNotification.objects.create(
        user=user,
        kind=NotificationKind.DUA,
        due_at=timezone.now() - timedelta(minutes=1),
        dedupe_key="due-test",
    )
    with patch("apps.notifications.tasks.async_task") as enqueue:
        assert dispatch_due_notifications() == 1
        assert dispatch_due_notifications() == 0
    notification.refresh_from_db()
    assert notification.status == "queued"
    enqueue.assert_called_once_with(
        "apps.notifications.tasks.deliver_notification", notification.id
    )


@pytest.mark.django_db
def test_delivery_records_message_id_and_is_idempotent(user):
    notification = ScheduledNotification.objects.create(
        user=user,
        kind=NotificationKind.DUA,
        due_at=timezone.now(),
        dedupe_key="delivery-test",
        status="queued",
    )
    sender = AsyncMock(return_value=4321)
    with patch("apps.telegram_bot.sender.send_scheduled_notification", sender):
        assert deliver_notification(notification.id) == 4321
        assert deliver_notification(notification.id) == 4321
    notification.refresh_from_db()
    assert notification.status == "sent"
    assert notification.telegram_message_id == 4321
    assert notification.attempts == 1
    sender.assert_awaited_once()


@pytest.mark.django_db
def test_weekly_report_aggregates_learning_and_qada(user, introduced_names):
    question = QuizQuestion.objects.create(
        user=user,
        target_name=introduced_names[0].name,
        quiz_type=QuizType.NAME_TO_MEANING,
        language="ru",
        prompt="x",
        options=[{"label": "x", "name_id": introduced_names[0].name_id}],
        correct_option=0,
    )
    QuizAttempt.objects.create(question=question, user=user, selected_option=0, is_correct=True)
    add_debt(user, WorshipKind.PRAYER, 1, PrayerType.FAJR)
    complete_one(user, WorshipKind.PRAYER, PrayerType.FAJR)
    report = build_weekly_report(user, timezone.localdate())
    assert report.data["reviews"] == 1
    assert report.data["accuracy"] == 100
    assert report.data["prayer_completed"] == 1
    assert "100%" in report.rendered_text


@pytest.mark.django_db
def test_weekly_report_includes_arabic_learning(user):
    from django.core.management import call_command

    call_command("seed_arabic", verbosity=0)
    lesson = ArabicLesson.objects.get(category="alphabet", order=1)
    complete_lesson(user, lesson.id)
    item = lesson.items.first()
    question = ArabicQuizQuestion.objects.create(
        user=user,
        target_item=item,
        quiz_type="arabic_meaning",
        language="ru",
        prompt=item.arabic_text,
        options=[{"label": "x", "item_id": item.id}],
        correct_option=0,
    )
    ArabicQuizAttempt.objects.create(
        question=question, user=user, selected_option=0, is_correct=True
    )
    report = build_weekly_report(user, timezone.localdate())
    assert report.data["arabic_lessons_completed"] == 1
    assert report.data["arabic_reviews"] == 1
    assert report.data["arabic_accuracy"] == 100
    assert "Арабский язык" in report.rendered_text


@pytest.mark.django_db
def test_weekly_schedule_respects_preference(user):
    pref = user.notification_preferences
    chosen = date(2026, 7, 26)
    pref.weekly_report_weekday = chosen.weekday()
    pref.save()
    assert plan_weekly_report_for_user(user, chosen).kind == NotificationKind.WEEKLY_REPORT
    assert plan_weekly_report_for_user(user, chosen + timedelta(days=1)) is None
