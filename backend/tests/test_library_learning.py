from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.api.account_services import AccountConflict, create_guest, reconcile_telegram_profile
from apps.content.models import Dua, DuaTranslation, Favorite, QuranPassage, QuranPassageTranslation
from apps.library_learning.models import LibraryQuizQuestion, LibraryQuizType, UserLibraryProgress
from apps.library_learning.services import (
    answer_library_quiz,
    build_library_quiz,
    confirm_library_studied,
    library_progress_stats,
)
from apps.users.models import TelegramUser

pytestmark = pytest.mark.django_db
API = "/api/v1/"


@pytest.fixture
def materials(source):
    result = {}
    for kind in ("ayah", "surah", "dua"):
        items = []
        for index in range(6):
            if kind == "dua":
                item = Dua.objects.create(
                    slug=f"dua-{index}", arabic_text=f"دعاء {index}", source=source
                )
            else:
                item = QuranPassage.objects.create(
                    slug=f"{kind}-{index}",
                    passage_type=kind,
                    surah_number=index + 1,
                    ayah_start=1,
                    ayah_end=1,
                    arabic_text=f"{kind} آية {index}",
                    source=source,
                )
            for language in ("uz", "ru", "en"):
                data = {
                    "language": language,
                    "title": f"{kind} {index} {language}",
                    "translation": f"Translation {kind} {index} {language}",
                }
                if kind == "dua":
                    DuaTranslation.objects.create(dua=item, **data)
                else:
                    QuranPassageTranslation.objects.create(passage=item, **data)
            items.append(item)
        result[kind] = items
    return result


def introduce(user, materials, kind, count=4):
    return [confirm_library_studied(user, kind, item.id)[0] for item in materials[kind][:count]]


@pytest.fixture
def web_client(user):
    user.auth_user = get_user_model().objects.create_user(username="library-owner", password=None)
    user.save(update_fields=["auth_user"])
    client = APIClient(enforce_csrf_checks=True)
    client.get(API + "auth/session/")
    client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
    client.force_login(user.auth_user)
    return client


@pytest.mark.parametrize("kind", ["ayah", "surah", "dua"])
@pytest.mark.parametrize("language", ["uz", "ru", "en"])
@pytest.mark.parametrize("quiz_type", LibraryQuizType.values[:4])
def test_four_quiz_types_use_only_studied_content_in_collection(
    user, materials, kind, language, quiz_type, monkeypatch
):
    user.language = language
    progress = introduce(user, materials, kind)
    introduce(user, materials, "dua" if kind != "dua" else "ayah")
    monkeypatch.setattr(
        "apps.library_learning.services.random.choice",
        lambda values: next(v for v in values if v[0] == quiz_type),
    )
    question = build_library_quiz(user, kind=kind)
    assert question.quiz_type == quiz_type and question.language == language
    assert len(question.options) == len({o["label"] for o in question.options}) == 4
    assert {o["progress_id"] for o in question.options} == {p.id for p in progress}
    assert question.options[question.correct_option]["progress_id"] == question.target_progress_id
    if quiz_type in ("meaning_arabic", "title_arabic"):
        assert language in question.prompt
    else:
        assert all(language in o["label"] for o in question.options)


def test_explicit_study_is_idempotent_and_less_than_four_is_locked(user, materials):
    rows = introduce(user, materials, "ayah", count=3)
    assert build_library_quiz(user, kind="ayah") is None
    row, created = confirm_library_studied(user, "ayah", materials["ayah"][0].id)
    assert not created and row.id == rows[0].id and row.next_review_at == rows[0].next_review_at
    assert UserLibraryProgress.objects.filter(user=user).count() == 3


def test_normal_review_uses_earliest_target_and_answer_is_idempotent(user, materials):
    rows = introduce(user, materials, "dua")
    due = timezone.now() - timedelta(days=1)
    UserLibraryProgress.objects.filter(id=rows[2].id).update(next_review_at=due)
    question = build_library_quiz(user, kind="dua")
    assert question.target_progress_id == rows[2].id
    assert answer_library_quiz(question.id, user, question.correct_option)[1]
    assert not answer_library_quiz(question.id, user, (question.correct_option + 1) % 4)[1]
    rows[2].refresh_from_db()
    assert rows[2].total_answers == rows[2].correct_answers == rows[2].review_stage == 1
    assert rows[2].next_review_at > timezone.now()
    assert library_progress_stats(user, "dua")["accuracy"] == 100


def test_incorrect_answer_resets_streak_and_extra_practice_keeps_schedule(user, materials):
    row = introduce(user, materials, "surah")[0]
    UserLibraryProgress.objects.filter(id=row.id).update(review_stage=3, correct_streak=2)
    question = build_library_quiz(user, kind="surah")
    answer_library_quiz(question.id, user, (question.correct_option + 1) % 4)
    row.refresh_from_db()
    assert row.correct_streak == 0 and row.review_stage == 2 and row.total_answers == 1
    dates = {
        p.id: (p.next_review_at, p.review_stage)
        for p in UserLibraryProgress.objects.filter(user=user)
    }
    extra = build_library_quiz(user, kind="surah", extra_practice=True)
    answer_library_quiz(extra.id, user, extra.correct_option)
    extra.target_progress.refresh_from_db()
    assert (extra.target_progress.next_review_at, extra.target_progress.review_stage) == dates[
        extra.target_progress_id
    ]
    assert library_progress_stats(user, "surah")["answers"] == 2


def test_unpublished_unstudied_and_other_users_content_are_excluded(user, materials):
    introduce(user, materials, "ayah")
    other = TelegramUser.objects.create(telegram_id=1002)
    introduce(other, materials, "ayah", count=6)
    materials["ayah"][0].is_published = False
    materials["ayah"][0].save(update_fields=["is_published"])
    assert build_library_quiz(user, kind="ayah") is None
    assert library_progress_stats(user, "ayah")["studied_count"] == 3
    with pytest.raises(QuranPassage.DoesNotExist):
        confirm_library_studied(user, "ayah", materials["ayah"][0].id)


def test_favorites_quiz_requires_four_studied_saved_items(user, materials):
    introduce(user, materials, "ayah")
    for item in materials["ayah"][:3]:
        Favorite.objects.create(user=user, passage=item)
    Favorite.objects.create(user=user, passage=materials["ayah"][4])
    assert build_library_quiz(user, kind="favorites") is None
    Favorite.objects.create(user=user, passage=materials["ayah"][3])
    question = build_library_quiz(user, kind="favorites")
    assert question and library_progress_stats(user, "favorites")["studied_count"] == 4


def test_duplicate_texts_never_generate_ambiguous_options(user, materials):
    introduce(user, materials, "dua")
    Dua.objects.filter(id__in=[i.id for i in materials["dua"][:4]]).update(arabic_text="Same text")
    # Identical Arabic answers cannot form four distinct options; identical Arabic prompts are ambiguous.
    assert build_library_quiz(user, kind="dua") is None


def test_question_keeps_original_answer_when_language_or_content_changes(user, materials):
    introduce(user, materials, "ayah")
    question = build_library_quiz(user, kind="ayah")
    translation = question.answer_translation
    user.language = "en"
    QuranPassageTranslation.objects.filter(passage=question.target_progress.passage).update(
        translation="Edited"
    )
    result, _ = answer_library_quiz(question.id, user, question.correct_option)
    assert (
        result.is_correct and result.language == "ru" and result.answer_translation == translation
    )


def test_api_study_quiz_answer_stats_and_no_answer_key_leak(user, materials, web_client):
    initial = web_client.get(API + "library/?kind=dua").json()
    assert not any(item["is_studied"] for item in initial["results"])
    for item in materials["dua"][:4]:
        route = API + f"library/dua/{item.id}/study/"
        assert web_client.post(route, {}, format="json").json() == {
            "created": True,
            "is_studied": True,
        }
        assert web_client.post(route, {}, format="json").json()["created"] is False
    public = web_client.post(API + "library/quiz/", {"kind": "dua"}, format="json").json()[
        "question"
    ]
    assert set(public) == {"id", "prompt", "quiz_type", "options", "audio_tracks"}
    assert all(set(option) == {"label"} for option in public["options"])
    question = LibraryQuizQuestion.objects.get(id=public["id"])
    route = API + f"library/quiz/{question.id}/answer/"
    assert web_client.post(route, {"selected_option": 4}, format="json").status_code == 400
    answered = web_client.post(route, {"selected_option": question.correct_option}, format="json")
    assert answered.json()["accepted"] and answered.json()["is_correct"]
    assert not web_client.post(route, {"selected_option": 0}, format="json").json()["accepted"]
    stats = web_client.get(API + "library/practice/?kind=dua").json()["stats"]
    assert stats == {
        "total_count": 6,
        "studied_count": 4,
        "due_count": 0,
        "answers": 1,
        "accuracy": 100,
        "audio_count": 0,
    }
    assert all(
        i["is_studied"] for i in web_client.get(API + "library/?kind=dua").json()["results"][:4]
    )


def test_api_auth_csrf_owner_and_kind_validation(user, materials, web_client):
    rows = introduce(user, materials, "ayah")
    question = build_library_quiz(user)
    bare = APIClient(enforce_csrf_checks=True)
    bare.force_login(user.auth_user)
    for route in [
        f"library/ayah/{materials['ayah'][0].id}/study/",
        "library/quiz/",
        f"library/quiz/{question.id}/answer/",
    ]:
        assert bare.post(API + route, {}, format="json").status_code == 403
    assert APIClient().get(API + "library/practice/").status_code == 403
    assert web_client.get(API + "library/practice/?kind=invalid").status_code == 400
    assert (
        web_client.post(API + "library/quiz/", {"kind": "invalid"}, format="json").status_code
        == 400
    )
    assert (
        web_client.post(
            API + f"library/surah/{materials['ayah'][0].id}/study/", {}, format="json"
        ).status_code
        == 404
    )
    _, guest = create_guest()
    web_client.force_login(guest.auth_user)
    route = API + f"library/quiz/{question.id}/answer/"
    assert (
        web_client.post(
            route, {"selected_option": question.correct_option}, format="json"
        ).status_code
        == 404
    )
    assert web_client.get(API + "library/practice/").json()["stats"]["studied_count"] == 0
    assert web_client.post(API + "library/quiz/", {}, format="json").json()["question"] is None
    assert (
        UserLibraryProgress.objects.filter(id__in=[r.id for r in rows], total_answers=0).count()
        == 4
    )


def test_telegram_linking_treats_library_history_as_real_progress(user, materials):
    _, guest = create_guest()
    introduce(guest, materials, "dua", 1)
    introduce(user, materials, "ayah", 1)
    with pytest.raises(AccountConflict):
        reconcile_telegram_profile(guest, user)
    guest.refresh_from_db()
    user.refresh_from_db()
    assert guest.is_active and user.is_active and user.telegram_id == 1001
    assert UserLibraryProgress.objects.count() == 2
