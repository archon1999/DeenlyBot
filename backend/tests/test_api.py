import hashlib
import hmac
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.db import close_old_connections, connection
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.api.auth_services import approve_browser_challenge
from apps.api.models import BrowserLoginChallenge
from apps.arabic_learning.models import ArabicLesson, ArabicQuizQuestion, UserArabicItemProgress
from apps.content.models import Dua, Favorite
from apps.learning.models import QuizAttempt, QuizQuestion, UserNameProgress
from apps.learning.services import answer_quiz, build_quiz
from apps.notifications.models import NotificationStatus, ScheduledNotification, WeeklyReport
from apps.users.models import NotificationPreference, TelegramUser
from apps.worship.models import FastOperationReceipt, QadaPrayer, QadaProfile, WorshipEntry
from apps.worship.services import record_fast_operation

API = "/api/v1/"


@pytest.fixture(autouse=True)
def clear_auth_throttles():
    cache.clear()


@pytest.fixture
def anon_client():
    client = APIClient(enforce_csrf_checks=True)
    response = client.get(f"{API}auth/session/")
    assert response.status_code == 200
    client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
    return client


@pytest.fixture
def owner_client(user, anon_client):
    account = get_user_model().objects.create_user(username="api-owner", password=None)
    user.auth_user = account
    user.save(update_fields=["auth_user"])
    anon_client.force_login(account)
    return anon_client


@pytest.fixture
def curriculum(db):
    call_command("seed_content", verbosity=0)
    call_command("seed_arabic", verbosity=0)


def post(client, route, data=None):
    return client.post(f"{API}{route}", data or {}, format="json")


def signed_init_data(telegram_id, *, age=0):
    data = {
        "auth_date": str(int(timezone.now().timestamp()) - age),
        "user": json.dumps({"id": telegram_id, "first_name": "Verified"}),
        "query_id": "test-query",
    }
    secret = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    data["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(data)


@pytest.mark.django_db
def test_csrf_applies_before_login_and_private_routes_require_owner(anon_client):
    unprotected = APIClient(enforce_csrf_checks=True)
    assert post(unprotected, "auth/telegram/start/").status_code == 403
    assert post(unprotected, "auth/miniapp/", {"init_data": "anything"}).status_code == 403
    for route in (
        "dashboard/",
        "names/",
        "arabic/",
        "qada/",
        "settings/",
        "reports/",
        "library/",
        "calendar/",
    ):
        assert anon_client.get(f"{API}{route}").status_code == 403
    assert anon_client.cookies["csrftoken"]["samesite"] == "Lax"


@pytest.mark.django_db
def test_authenticated_mutations_still_require_csrf(user, owner_client, four_names):
    without_csrf = APIClient(enforce_csrf_checks=True)
    without_csrf.force_login(user.auth_user)
    assert post(without_csrf, f"names/{four_names[0].id}/confirm/").status_code == 403
    assert (
        without_csrf.patch(f"{API}settings/", {"language": "en"}, format="json").status_code == 403
    )
    assert post(without_csrf, "auth/logout/").status_code == 403
    assert UserNameProgress.objects.count() == 0


@pytest.mark.django_db
def test_browser_login_is_bound_single_use_and_has_unusable_password(user, anon_client):
    started = post(anon_client, "auth/telegram/start/")
    assert started.status_code == 200
    token = parse_qs(urlparse(started.json()["telegram_url"]).query)["start"][0][4:]
    assert len(f"web_{token}") <= 64
    challenge = BrowserLoginChallenge.objects.get()
    assert challenge.token_hash != token
    assert post(anon_client, "auth/telegram/complete/").status_code == 202
    other_browser = APIClient(enforce_csrf_checks=True)
    other_browser.get(f"{API}auth/session/")
    other_browser.defaults["HTTP_X_CSRFTOKEN"] = other_browser.cookies["csrftoken"].value
    assert post(other_browser, "auth/telegram/complete/").status_code == 400
    approve_browser_challenge(token, user, login_consent=True)
    completed = post(anon_client, "auth/telegram/complete/")
    assert completed.status_code == 200
    assert completed.json()["profile"]["id"] == user.id
    user.refresh_from_db()
    assert user.auth_user.has_usable_password() is False
    assert anon_client.get(f"{API}auth/session/").json()["authenticated"] is True
    anon_client.defaults["HTTP_X_CSRFTOKEN"] = anon_client.cookies["csrftoken"].value
    assert post(anon_client, "auth/telegram/complete/").status_code == 400
    assert post(anon_client, "auth/logout/").status_code == 200
    assert anon_client.get(f"{API}auth/session/").json()["authenticated"] is False


@pytest.mark.django_db
def test_expired_challenge_and_nonowner_approval_rejected(user, anon_client):
    started = post(anon_client, "auth/telegram/start/").json()
    token = parse_qs(urlparse(started["telegram_url"]).query)["start"][0][4:]
    user.is_owner = False
    with pytest.raises(ValueError, match="owner"):
        approve_browser_challenge(token, user)
    user.is_owner = True
    BrowserLoginChallenge.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    with pytest.raises(ValueError, match="expired"):
        approve_browser_challenge(token, user)
    assert post(anon_client, "auth/telegram/complete/").status_code == 400


@pytest.mark.django_db
def test_login_start_throttles_excess_requests(anon_client):
    for _ in range(10):
        assert post(anon_client, "auth/telegram/start/").status_code == 200
    assert post(anon_client, "auth/telegram/start/").status_code == 429


@pytest.mark.django_db
def test_miniapp_raw_signature_freshness_identity_and_disabled_account(user, anon_client):
    valid = signed_init_data(user.telegram_id)
    for invalid in (
        "not-a-query-string",
        "hash=x&auth_date=x&user=[]",
        valid.replace("Verified", "Tampered"),
        signed_init_data(user.telegram_id, age=700),
        signed_init_data(user.telegram_id, age=-100),
        signed_init_data(99999),
        valid + "&auth_date=1",
    ):
        assert post(anon_client, "auth/miniapp/", {"init_data": invalid}).status_code == 400
    assert post(anon_client, "auth/miniapp/", {"init_data": valid}).status_code == 200
    user.refresh_from_db()
    user.auth_user.is_active = False
    user.auth_user.save(update_fields=["is_active"])
    assert anon_client.get(f"{API}auth/session/").json()["authenticated"] is False
    anon_client.defaults["HTTP_X_CSRFTOKEN"] = anon_client.cookies["csrftoken"].value
    assert post(anon_client, "auth/miniapp/", {"init_data": valid}).status_code == 400


@pytest.mark.django_db
def test_inactive_profile_denied_while_website_permission_does_not_bypass_bot_guard(
    user, owner_client
):
    user.is_active = False
    user.save(update_fields=["is_active"])
    assert owner_client.get(f"{API}dashboard/").status_code == 403
    assert owner_client.get(f"{API}auth/session/").json()["authenticated"] is False
    user.is_active = True
    user.save(update_fields=["is_active"])
    with override_settings(BOT_OWNER_TELEGRAM_ID=99999):
        assert owner_client.get(f"{API}names/").status_code == 200
        assert (
            post(
                owner_client, "auth/miniapp/", {"init_data": signed_init_data(user.telegram_id)}
            ).status_code
            == 400
        )


@pytest.mark.django_db
def test_names_sequential_confirm_and_private_quiz_answers(user, owner_client, four_names):
    assert post(owner_client, "names/quiz/").json()["question"] is None
    assert post(owner_client, f"names/{four_names[-1].id}/confirm/").status_code == 400
    for name in four_names:
        assert post(owner_client, f"names/{name.id}/confirm/").json()["created"] is True
        assert post(owner_client, f"names/{name.id}/confirm/").json()["created"] is False
    question_dto = post(owner_client, "names/quiz/").json()["question"]
    assert set(question_dto) == {"id", "prompt", "quiz_type", "options", "audio_tracks"}
    assert all(set(option) == {"label"} for option in question_dto["options"])
    question = QuizQuestion.objects.get(id=question_dto["id"])
    answer = post(
        owner_client,
        f"names/quiz/{question.id}/answer/",
        {"selected_option": question.correct_option},
    )
    assert answer.json()["accepted"] is True
    assert answer.json()["is_correct"] is True
    repeat = post(
        owner_client,
        f"names/quiz/{question.id}/answer/",
        {"selected_option": (question.correct_option + 1) % 4},
    )
    assert repeat.json()["accepted"] is False
    assert repeat.json()["is_correct"] is True
    assert QuizAttempt.objects.count() == 1
    other = TelegramUser.objects.create(telegram_id=9900)
    foreign_question = QuizQuestion.objects.create(
        user=other,
        target_name=four_names[0],
        quiz_type="name_meaning",
        language="ru",
        prompt="Foreign",
        options=[{"label": "no"}],
        correct_option=0,
    )
    assert (
        post(
            owner_client, f"names/quiz/{foreign_question.id}/answer/", {"selected_option": 0}
        ).status_code
        == 404
    )


@pytest.mark.django_db
def test_arabic_lessons_quiz_and_report_share_bot_progress(user, owner_client, curriculum):
    lessons = owner_client.get(f"{API}arabic/").json()["lessons"]
    assert len(lessons) == 62
    assert {lesson["category"] for lesson in lessons} == {
        "alphabet",
        "quran_vocabulary",
        "grammar",
        "prayer_arabic",
        "sarf",
        "daily_phrases",
        "listening",
    }
    first_two = list(ArabicLesson.objects.filter(category="alphabet")[:2])
    for lesson in first_two:
        detail = owner_client.get(f"{API}arabic/lessons/{lesson.id}/").json()
        assert detail["items"][0]["transcription"]
        assert (
            post(owner_client, f"arabic/lessons/{lesson.id}/start/").json()["status"]
            == "in_progress"
        )
        assert (
            post(owner_client, f"arabic/lessons/{lesson.id}/complete/").json()["status"]
            == "completed"
        )
    question_dto = post(owner_client, "arabic/quiz/").json()["question"]
    assert set(question_dto) == {"id", "prompt", "quiz_type", "options", "audio_tracks"}
    question = ArabicQuizQuestion.objects.get(id=question_dto["id"])
    assert (
        post(
            owner_client,
            f"arabic/quiz/{question.id}/answer/",
            {"selected_option": question.correct_option},
        ).json()["is_correct"]
        is True
    )
    assert (
        post(
            owner_client,
            f"arabic/quiz/{question.id}/answer/",
            {"selected_option": question.correct_option},
        ).json()["accepted"]
        is False
    )
    assert (
        sum(
            UserArabicItemProgress.objects.filter(user=user).values_list("total_answers", flat=True)
        )
        == 1
    )
    assert owner_client.get(f"{API}reports/").json()["stats"]["arabic_lessons_completed"] == 2


@pytest.mark.django_db
def test_library_kind_pagination_language_search_and_explicit_favorite(
    user, owner_client, curriculum
):
    user.language = "uz"
    user.save(update_fields=["language"])
    response = owner_client.get(f"{API}library/?kind=ayah").json()
    assert (response["count"], response["pages"], len(response["results"])) == (11, 2, 10)
    second = owner_client.get(f"{API}library/?kind=ayah&page=2").json()
    assert len(second["results"]) == 1
    assert owner_client.get(f"{API}library/?kind=surah").json()["count"] == 10
    assert owner_client.get(f"{API}library/?kind=dua").json()["count"] == 27
    item = response["results"][0]
    route = f"library/ayah/{item['id']}/favorite/"
    assert post(owner_client, route, {"saved": True}).json() == {"saved": True}
    assert post(owner_client, route, {"saved": True}).json() == {"saved": True}
    assert Favorite.objects.filter(user=user).count() == 1
    assert owner_client.get(f"{API}library/?kind=favorites").json()["count"] == 1
    assert post(owner_client, route, {"saved": False}).json() == {"saved": False}
    assert Favorite.objects.count() == 0
    assert owner_client.get(f"{API}library/?kind=ayah&q=not-a-real-verse").json()["count"] == 0
    assert owner_client.get(f"{API}library/?kind=ayah&page=0").status_code == 400
    assert (
        post(owner_client, f"library/surah/{item['id']}/favorite/", {"saved": True}).status_code
        == 404
    )
    dua = Dua.objects.first()
    assert (
        post(owner_client, f"library/dua/{dua.id}/favorite/", {"saved": True}).json()["saved"]
        is True
    )


@pytest.mark.django_db
def test_qada_manual_priority_stale_key_no_witr_and_fast_receipts(owner_client):
    response = post(
        owner_client, "qada/configure/", {"start_date": "2026-05-23", "start_prayer": "fajr"}
    )
    assert response.status_code == 200
    historical_key = response.json()["current"]["key"]
    for prayer_type in ("fajr", "isha"):
        assert (
            post(
                owner_client, "qada/add/", {"prayer_date": "2026-07-27", "prayer_type": prayer_type}
            ).status_code
            == 200
        )
    assert (
        post(
            owner_client, "qada/add/", {"prayer_date": "2026-07-27", "prayer_type": "witr"}
        ).status_code
        == 400
    )
    assert post(owner_client, "qada/complete/").status_code == 400
    assert post(owner_client, "qada/complete/", {"expected_key": historical_key}).status_code == 409
    current = owner_client.get(f"{API}qada/").json()["current"]
    assert current["prayer_type"] == "isha"
    assert (
        post(owner_client, "qada/complete/", {"expected_key": current["key"]}).json()["current"][
            "prayer_type"
        ]
        == "fajr"
    )
    assert post(owner_client, "qada/complete/", {"expected_key": current["key"]}).status_code == 409
    operation = {"action": "add", "amount": 3, "operation_id": str(uuid.uuid4())}
    assert post(owner_client, "qada/fast/", operation).json()["fast_balance"] == 3
    assert post(owner_client, "qada/fast/", operation).json()["fast_balance"] == 3
    assert post(owner_client, "qada/fast/", {**operation, "amount": 4}).status_code == 409
    completion = {"action": "complete", "operation_id": str(uuid.uuid4())}
    assert post(owner_client, "qada/fast/", completion).json()["fast_balance"] == 2
    assert post(owner_client, "qada/fast/", completion).json()["fast_balance"] == 2
    assert FastOperationReceipt.objects.count() == 2


@pytest.mark.django_db
def test_api_gets_do_not_create_progress_debt_or_reports(user, owner_client, curriculum):
    model_classes = (
        UserNameProgress,
        UserArabicItemProgress,
        QadaProfile,
        QadaPrayer,
        WorshipEntry,
        Favorite,
        WeeklyReport,
    )
    before = {model: model.objects.count() for model in model_classes}
    for route in (
        "dashboard/",
        "names/",
        "arabic/",
        "qada/",
        "settings/",
        "reports/",
        "library/",
        "calendar/",
    ):
        response = owner_client.get(f"{API}{route}?user_id=9999")
        assert response.status_code == 200
    assert owner_client.get(f"{API}calendar/").json()["events"]
    assert {model: model.objects.count() for model in model_classes} == before
    first_lesson = ArabicLesson.objects.first()
    assert owner_client.get(f"{API}arabic/lessons/{first_lesson.id}/").status_code == 200
    assert UserArabicItemProgress.objects.count() == 0


@pytest.mark.django_db
def test_settings_validate_whole_form_and_replan_after_commit(
    user, owner_client, django_capture_on_commit_callbacks
):
    assert (
        owner_client.patch(
            f"{API}settings/", {"random_window_start": "09:15"}, format="json"
        ).status_code
        == 400
    )
    assert (
        owner_client.patch(
            f"{API}settings/", {"random_window_end": "08:00"}, format="json"
        ).status_code
        == 400
    )
    assert (
        owner_client.patch(
            f"{API}settings/", {"timezone": "invalid/zone"}, format="json"
        ).status_code
        == 400
    )
    assert (
        owner_client.patch(f"{API}settings/", {"is_owner": False}, format="json").status_code == 400
    )
    fixed_now = timezone.now().replace(hour=3, minute=0, second=0, microsecond=0)
    with patch("django.utils.timezone.now", return_value=fixed_now):
        with django_capture_on_commit_callbacks(execute=True):
            response = owner_client.patch(
                f"{API}settings/",
                {
                    "language": "en",
                    "random_messages_per_day": 3,
                    "random_window_start": "09:30",
                    "weekly_report_enabled": False,
                },
                format="json",
            )
    assert response.status_code == 200
    assert response.json()["random_window_start"] == "09:30"
    user.refresh_from_db()
    assert user.language == "en"
    preference = NotificationPreference.objects.get(user=user)
    assert preference.schedule_version == 1
    scheduled = ScheduledNotification.objects.filter(user=user, status=NotificationStatus.PENDING)
    assert scheduled.count() == 3
    assert {item.due_at.minute for item in scheduled} <= {0, 30}


@pytest.mark.django_db(transaction=True)
def test_concurrent_quiz_answers_and_fast_receipts_apply_once(user, introduced_names):
    if connection.vendor == "sqlite":
        assert connection.transaction_mode == "IMMEDIATE"
    question = build_quiz(user)

    def answer_in_thread():
        close_old_connections()
        try:
            return answer_quiz(question.id, user, question.correct_option)[1]
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: answer_in_thread(), range(2)))
    assert sorted(results) == [False, True]
    assert QuizAttempt.objects.count() == 1
    assert sum(UserNameProgress.objects.values_list("total_answers", flat=True)) == 1
    operation_id = uuid.uuid4()

    def fast_in_thread():
        close_old_connections()
        try:
            return record_fast_operation(user, operation_id, "add", 2)[1]
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: fast_in_thread(), range(2)))
    assert sorted(results) == [False, True]
    assert FastOperationReceipt.objects.count() == 1
    assert WorshipEntry.objects.filter(user=user).count() == 1


@pytest.mark.django_db(transaction=True)
def test_bot_start_deeplink_uses_verified_db_owner(user, anon_client):
    started = post(anon_client, "auth/telegram/start/").json()
    payload = parse_qs(urlparse(started["telegram_url"]).query)["start"][0]
    import asyncio

    from apps.telegram_bot.handlers import confirm_website_login, start

    message = SimpleNamespace(text=f"/start {payload}", answer=AsyncMock(), edit_text=AsyncMock())

    async def exercise():
        try:
            await start(message, user)
            assert (
                await sync_to_async(
                    lambda: BrowserLoginChallenge.objects.get().approved_by_id,
                    thread_sensitive=True,
                )()
                is None
            )
            assert (
                await sync_to_async(
                    lambda: post(anon_client, "auth/telegram/complete/"), thread_sensitive=True
                )()
            ).status_code == 202
            callback = SimpleNamespace(
                data=f"web_login:{payload[4:]}", message=message, answer=AsyncMock()
            )
            await confirm_website_login(callback, user)
        finally:
            await sync_to_async(close_old_connections, thread_sensitive=True)()

    asyncio.run(exercise())
    assert message.answer.await_count == 1
    assert BrowserLoginChallenge.objects.get().approved_by_id == user.id
