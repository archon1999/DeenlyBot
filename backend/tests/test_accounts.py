import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.api.account_services import register_account
from apps.api.auth_services import approve_browser_challenge
from apps.api.models import BrowserLoginChallenge
from apps.arabic_learning.models import ArabicLesson
from apps.learning.models import UserNameProgress
from apps.notifications.models import ScheduledNotification
from apps.notifications.services import (
    plan_daily_for_user,
    plan_event_reminders_for_user,
    plan_weekly_report_for_user,
)
from apps.notifications.tasks import deliver_notification, plan_daily_notifications
from apps.users.models import AccountCredential, TelegramUser
from apps.users.services import PersonalBotAccessDenied, register_or_update_telegram_user

BASE = "/api/v1/"
PASSWORD = "Sahifa!2026Uz"


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


def browser():
    client = APIClient(enforce_csrf_checks=True)
    assert client.get(BASE + "auth/session/").status_code == 200
    return client


def post(client, route, data=None):
    return client.post(
        BASE + route, data or {}, format="json", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value
    )


def register(client, email="member@example.com"):
    return post(
        client, "auth/register/", {"first_name": "Member", "email": email, "password": PASSWORD}
    )


def start_link(client):
    response = post(client, "auth/telegram/link/start/")
    assert response.status_code == 200
    return parse_qs(urlparse(response.json()["telegram_url"]).query)["start"][0][4:]


@pytest.mark.django_db
def test_guest_upgrade_preserves_id_auth_user_progress_and_separate_website_scopes(four_names):
    first, other = browser(), browser()
    started = post(first, "auth/guest/", {"language": "en"})
    profile = started.json()["profile"]
    assert profile["is_guest"] is True and profile["telegram_linked"] is False
    guest = TelegramUser.objects.get(id=profile["id"])
    assert guest.telegram_id is None and guest.is_owner is False
    account_id = guest.auth_user_id
    assert post(first, "auth/guest/").json()["profile"]["id"] == guest.id
    assert post(first, f"names/{four_names[0].id}/confirm/").json()["created"] is True
    assert post(other, "auth/guest/").json()["profile"]["id"] != guest.id
    assert other.get(BASE + "names/").json()["introduced_count"] == 0
    upgraded = register(first, "MEMBER@Example.com")
    assert upgraded.status_code == 200
    assert upgraded.json()["profile"]["id"] == guest.id
    assert upgraded.json()["profile"]["account_kind"] == "member"
    assert upgraded.json()["profile"]["email"] == "member@example.com"
    guest.refresh_from_db()
    assert guest.auth_user_id == account_id
    assert guest.auth_user.check_password(PASSWORD)
    assert guest.auth_user.password != PASSWORD
    assert first.get(BASE + "names/").json()["introduced_count"] == 1
    post(first, "auth/logout/")
    assert (
        post(
            first, "auth/login/", {"email": "MeMbEr@example.COM", "password": PASSWORD}
        ).status_code
        == 200
    )
    assert first.get(BASE + "names/").json()["introduced_count"] == 1


@pytest.mark.django_db
def test_credentials_csrf_password_validation_duplicate_email_and_profile_permissions():
    bare = APIClient(enforce_csrf_checks=True)
    for route in ("auth/guest/", "auth/register/", "auth/login/"):
        assert bare.post(BASE + route, {}, format="json").status_code == 403
    client, other = browser(), browser()
    assert (
        post(
            client,
            "auth/register/",
            {"email": "valid@example.com", "first_name": "Member", "password": "12345678"},
        ).status_code
        == 400
    )
    assert AccountCredential.objects.count() == 0
    response = register(client)
    assert response.status_code == 200
    assert register(other, "MEMBER@example.com").status_code == 400
    assert (
        post(other, "auth/login/", {"email": "member@example.com", "password": "wrong"}).json()
        == post(other, "auth/login/", {"email": "missing@example.com", "password": "wrong"}).json()
    )
    changed = client.patch(
        BASE + "auth/profile/",
        {"first_name": "New name", "language": "uz"},
        format="json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )
    assert changed.json()["profile"]["first_name"] == "New name"
    assert (
        client.patch(
            BASE + "auth/profile/",
            {"is_owner": True, "telegram_id": 77},
            format="json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        ).status_code
        == 400
    )
    profile = TelegramUser.objects.get(id=response.json()["profile"]["id"])
    profile.is_active = False
    profile.save(update_fields=["is_active"])
    assert client.get(BASE + "auth/profile/").status_code == 403
    assert (
        post(
            other, "auth/login/", {"email": "member@example.com", "password": PASSWORD}
        ).status_code
        == 400
    )


@pytest.mark.django_db
def test_guest_has_no_notification_jobs_or_send_target_even_if_preferences_enabled():
    client = browser()
    profile_id = post(client, "auth/guest/").json()["profile"]["id"]
    profile = TelegramUser.objects.get(pk=profile_id)
    pref = profile.notification_preferences
    pref.enabled, pref.weekly_report_enabled = True, True
    pref.save()
    assert plan_daily_for_user(profile) == []
    assert plan_event_reminders_for_user(profile) == []
    assert plan_weekly_report_for_user(profile) is None
    assert plan_daily_notifications() == 0
    assert ScheduledNotification.objects.count() == 0
    notification = ScheduledNotification.objects.create(
        user=profile, kind="dua", due_at=timezone.now(), dedupe_key="guest-no-send", status="queued"
    )
    with patch("apps.telegram_bot.sender.send_scheduled_notification") as send:
        assert deliver_notification(notification.id) is None
        send.assert_not_called()
    notification.refresh_from_db()
    assert notification.status == "skipped"


@pytest.mark.django_db
def test_guest_records_do_not_claim_personal_bot_owner():
    client = browser()
    post(client, "auth/guest/")
    verified = SimpleNamespace(
        id=555, username="verified", first_name="Verified", last_name="", language_code="uz"
    )
    with override_settings(BOT_OWNER_TELEGRAM_ID=555, PERSONAL_BOT_MODE=True):
        owner = register_or_update_telegram_user(verified)
        assert owner.is_owner is True
        with pytest.raises(PersonalBotAccessDenied):
            register_or_update_telegram_user(SimpleNamespace(**{**verified.__dict__, "id": 556}))
    assert TelegramUser.objects.filter(telegram_id__isnull=True).count() == 1


@pytest.mark.django_db
def test_verified_link_keeps_guest_progress_when_telegram_identity_is_empty(user, four_names):
    client = browser()
    profile_id = post(client, "auth/guest/").json()["profile"]["id"]
    post(client, f"names/{four_names[0].id}/confirm/")
    token = start_link(client)
    assert post(client, "auth/telegram/link/complete/").status_code == 202
    approve_browser_challenge(token, user, link_consent=True)
    completed = post(client, "auth/telegram/link/complete/")
    assert completed.status_code == 200
    assert completed.json()["profile"]["id"] == profile_id
    assert completed.json()["profile"]["telegram_linked"] is True
    assert client.get(BASE + "names/").json()["introduced_count"] == 1
    user.refresh_from_db()
    assert user.is_active is False and user.telegram_id is None
    assert post(client, "auth/telegram/link/complete/").status_code == 400


@pytest.mark.django_db
def test_verified_legacy_link_keeps_existing_progress_and_rebinds_empty_member(user, four_names):
    now = timezone.now()
    progress = UserNameProgress.objects.create(
        user=user, name=four_names[0], introduced_at=now, next_review_at=now
    )
    old_account = get_user_model().objects.create_user(username="legacy", password=None)
    user.auth_user = old_account
    user.save(update_fields=["auth_user"])
    client = browser()
    registered = register(client).json()["profile"]
    empty_profile_id = registered["id"]
    token = start_link(client)
    approve_browser_challenge(token, user, link_consent=True)
    linked = post(client, "auth/telegram/link/complete/")
    assert linked.status_code == 200
    assert linked.json()["profile"]["id"] == user.id
    assert linked.json()["profile"]["email"] == "member@example.com"
    progress.refresh_from_db()
    assert progress.user_id == user.id
    assert client.get(BASE + "names/").json()["introduced_count"] == 1
    assert TelegramUser.objects.get(pk=empty_profile_id).is_active is False
    old_account.refresh_from_db()
    assert old_account.is_active is False
    post(client, "auth/logout/")
    assert (
        post(client, "auth/login/", {"email": "member@example.com", "password": PASSWORD}).json()[
            "profile"
        ]["id"]
        == user.id
    )


@pytest.mark.django_db
def test_link_conflicts_leave_both_progress_and_registered_identity_untouched(user, four_names):
    client = browser()
    member = register(client).json()["profile"]
    post(client, f"names/{four_names[0].id}/confirm/")
    now = timezone.now()
    UserNameProgress.objects.create(
        user=user, name=four_names[0], introduced_at=now, next_review_at=now
    )
    token = start_link(client)
    approve_browser_challenge(token, user, link_consent=True)
    response = post(client, "auth/telegram/link/complete/")
    assert response.status_code == 409 and response.json()["code"] == "both_profiles_have_progress"
    assert UserNameProgress.objects.count() == 2
    user.refresh_from_db()
    assert user.telegram_id == 1001 and user.is_active
    assert client.get(BASE + "auth/profile/").json()["profile"]["id"] == member["id"]
    account = get_user_model().objects.create_user(
        username="registered-telegram", password=PASSWORD
    )
    user.auth_user = account
    user.save(update_fields=["auth_user"])
    response = post(client, "auth/telegram/link/complete/")
    assert response.status_code == 409 and response.json()["code"] == "registered_telegram_account"


@pytest.mark.django_db
def test_link_challenge_wrong_account_wrong_purpose_and_expiry_rejected(user):
    first, other = browser(), browser()
    register(first, "first@example.com")
    register(other, "other@example.com")
    token = start_link(first)
    approve_browser_challenge(token, user, link_consent=True)
    challenge_id = first.session["telegram_login_challenge"]
    binding = first.session["telegram_login_binding"]
    wrong_session = other.session
    wrong_session["telegram_login_challenge"] = challenge_id
    wrong_session["telegram_login_binding"] = binding
    wrong_session.save()
    assert post(other, "auth/telegram/link/complete/").status_code == 400
    assert post(first, "auth/telegram/complete/").status_code == 400
    BrowserLoginChallenge.objects.filter(pk=challenge_id).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    assert post(first, "auth/telegram/link/complete/").status_code == 400


@pytest.mark.django_db
def test_disabled_legacy_auth_account_cannot_be_reactivated_by_linking(user):
    account = get_user_model().objects.create_user(username="disabled-legacy", password=None)
    account.is_active = False
    account.save(update_fields=["is_active"])
    user.auth_user = account
    user.save(update_fields=["auth_user"])
    client = browser()
    register(client)
    token = start_link(client)
    approve_browser_challenge(token, user, link_consent=True)
    response = post(client, "auth/telegram/link/complete/")
    assert response.status_code == 409
    assert response.json()["code"] == "disabled_telegram_account"
    account.refresh_from_db()
    assert account.is_active is False


@pytest.mark.django_db(transaction=True)
def test_case_insensitive_email_race_allows_only_one_account_and_db_constraint():
    def attempt(email):
        close_old_connections()
        try:
            register_account(email=email, password=PASSWORD, first_name="Member")
            return "created"
        except ValidationError:
            return "duplicate"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(attempt, ["Race@example.com", "race@EXAMPLE.COM"])) == [
            "created",
            "duplicate",
        ]
    assert AccountCredential.objects.count() == 1
    second = get_user_model().objects.create_user(username="other")
    with pytest.raises(IntegrityError), transaction.atomic():
        AccountCredential.objects.create(user=second, email="RACE@example.COM")


@pytest.mark.django_db
def test_login_throttle_cannot_be_reset_with_forwarding_headers():
    client = browser()
    for index in range(20):
        response = client.post(
            BASE + "auth/login/",
            {"email": f"missing{index}@example.com", "password": "wrong"},
            format="json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
            HTTP_X_FORWARDED_FOR=f"spoof-{index}",
        )
        assert response.status_code == 400
    response = client.post(
        BASE + "auth/login/",
        {"email": "new-missing@example.com", "password": "wrong"},
        format="json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        HTTP_X_FORWARDED_FOR="another-client",
    )
    assert response.status_code == 429


@pytest.mark.django_db
def test_arabic_preview_is_real_curriculum_and_prefetched_without_per_lesson_reads():
    call_command("seed_arabic", verbosity=0)
    client = browser()
    post(client, "auth/guest/")
    with CaptureQueriesContext(connection) as captured:
        response = client.get(BASE + "arabic/")
    assert response.status_code == 200
    assert len(captured) < 20
    for dto in response.json()["lessons"]:
        lesson = ArabicLesson.objects.get(pk=dto["id"])
        assert dto["preview_arabic"] == [
            item.arabic_text for item in list(lesson.items.all())[:2] if item.arabic_text
        ]


@pytest.mark.django_db
def test_custom_profile_name_is_not_overwritten_by_next_bot_event(user):
    client = browser()
    account = get_user_model().objects.create_user(username="display-owner", password=None)
    user.auth_user = account
    user.save(update_fields=["auth_user"])
    client.force_login(account)
    response = client.patch(
        BASE + "auth/profile/",
        {"first_name": "My chosen name"},
        format="json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )
    assert response.status_code == 200
    telegram_sender = SimpleNamespace(
        id=user.telegram_id,
        username="changed",
        first_name="Telegram name",
        last_name="",
        language_code="ru",
    )
    register_or_update_telegram_user(telegram_sender)
    user.refresh_from_db()
    assert user.first_name == "My chosen name" and user.username == "changed"


@pytest.mark.django_db(transaction=True)
def test_bot_link_displays_destination_and_requires_explicit_confirmation(user):
    client = browser()
    register(client)
    token = start_link(client)
    with pytest.raises(ValueError, match="confirmation"):
        approve_browser_challenge(token, user)
    from apps.telegram_bot.handlers import confirm_website_link, start

    message = SimpleNamespace(text=f"/start web_{token}", answer=AsyncMock(), edit_text=AsyncMock())
    callback = SimpleNamespace(data=f"web_link:{token}", message=message, answer=AsyncMock())

    # Assert DB state outside the event loop, where synchronous ORM reads are valid.
    async def run_adapter():
        try:
            await start(message, user)
            assert "member@example.com" in message.answer.call_args.args[0]
            assert (
                await sync_to_async(
                    lambda: BrowserLoginChallenge.objects.filter(approved_by__isnull=False).count(),
                    thread_sensitive=True,
                )()
                == 0
            )
            await confirm_website_link(callback, user)
        finally:
            await sync_to_async(close_old_connections, thread_sensitive=True)()

    asyncio.run(run_adapter())
    assert BrowserLoginChallenge.objects.get().approved_by_id == user.id
    assert post(client, "auth/telegram/link/complete/").status_code == 200
