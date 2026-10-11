from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.api.dto import quiz_dto
from apps.arabic_learning.models import (
    ArabicItemTranslation,
    ArabicLearningItem,
    ArabicLesson,
    ArabicQuizQuestion,
    UserArabicItemProgress,
)
from apps.arabic_learning.services import answer_arabic_quiz, build_arabic_quiz
from apps.content.models import QuranPassage, QuranPassageTranslation
from apps.library_learning.models import LibraryQuizQuestion
from apps.library_learning.services import (
    answer_library_quiz,
    build_library_quiz,
    confirm_library_studied,
)
from apps.study_media.models import AudioAsset, AudioBinding
from apps.users.models import TelegramUser

pytestmark = pytest.mark.django_db


def _audio(source, index, **target):
    asset = AudioAsset.objects.create(
        key=f"test-listening-{index}",
        url=f"https://recordings.example.org/{index}.mp3",
        voice="Reviewed speaker",
        source=source,
        attribution="Public recording credit",
        license_notes="Permission confirmed in isolated test",
        rights_confirmed=True,
        pronunciation_verified=True,
        is_published=True,
        available=True,
        segments=[{"key": "answer-token", "label": "ANSWER LEAK", "start_ms": 0, "end_ms": 1000}],
    )
    AudioBinding.objects.create(
        asset=asset, label={"uz": "ANSWER LEAK", "en": "ANSWER LEAK", "ru": "ANSWER LEAK"}, **target
    )
    return asset


@pytest.fixture
def pool(user, source):
    now = timezone.now() - timedelta(hours=1)
    lesson = ArabicLesson.objects.create(
        slug="audio-test", category="listening", order=1, source=source
    )
    rows = {"arabic": [], "library": []}
    for index in range(5):
        item = ArabicLearningItem.objects.create(
            lesson=lesson, order=index + 1, item_type="word", arabic_text=f"كلمة {index}"
        )
        passage = QuranPassage.objects.create(
            slug=f"audio-passage-{index}",
            surah_number=2,
            ayah_start=index + 1,
            ayah_end=index + 1,
            arabic_text=f"آية {index}",
            source=source,
        )
        for language in ("uz", "en", "ru"):
            ArabicItemTranslation.objects.create(
                item=item,
                language=language,
                title=f"Item {index}",
                meaning=f"Meaning {index} {language}",
                transcription=f"Sound {index}",
            )
            QuranPassageTranslation.objects.create(
                passage=passage,
                language=language,
                title=f"Passage {index}",
                translation=f"Meaning {index} {language}",
                transcription=f"Sound {index}",
            )
        arabic_asset = _audio(source, f"ar-{index}", arabic_item=item)
        library_asset = _audio(source, f"lib-{index}", passage=passage)
        if index < 4:
            row = UserArabicItemProgress.objects.create(
                user=user, item=item, introduced_at=now, next_review_at=now
            )
            library_row, _ = confirm_library_studied(user, "ayah", passage.id)
            rows["arabic"].append((row, arabic_asset))
            rows["library"].append((library_row, library_asset))
    return rows


@pytest.mark.parametrize("kind", ["arabic", "library"])
@pytest.mark.parametrize("language", ["uz", "ru", "en"])
@pytest.mark.parametrize("quiz_type", ["audio_arabic", "audio_meaning"])
def test_listening_four_options_are_owned_studied_audio_enabled_and_no_captions_leak(
    user, pool, kind, language, quiz_type, monkeypatch
):
    user.language = language
    monkeypatch.setattr(
        f"apps.{'arabic_learning' if kind == 'arabic' else 'library_learning'}.services.random.choice",
        lambda values: next(row for row in values if row[0] == quiz_type),
    )
    question = (
        build_arabic_quiz(user, mode="listening")
        if kind == "arabic"
        else build_library_quiz(user, mode="listening")
    )
    assert question and question.quiz_type == quiz_type
    options_key = "item_id" if kind == "arabic" else "progress_id"
    ids = {row.item_id if kind == "arabic" else row.id for row, _ in pool[kind]}
    assert {option[options_key] for option in question.options} == ids
    public = quiz_dto(question)
    assert (
        len(public["options"]) == 4 and len({option["label"] for option in public["options"]}) == 4
    )
    assert "ANSWER LEAK" not in str(public)
    assert public["audio_tracks"][0]["segments"] == []
    assert "target" not in public and "correct_option" not in public
    assert public["prompt"] not in [option["label"] for option in public["options"]]


@pytest.mark.parametrize("kind", ["arabic", "library"])
def test_unavailable_or_unreviewed_asset_removes_candidate_without_network(user, pool, kind):
    asset = pool[kind][0][1]
    asset.rights_confirmed = False
    asset.save(update_fields=["rights_confirmed"])
    question = (
        build_arabic_quiz(user, mode="listening")
        if kind == "arabic"
        else build_library_quiz(user, mode="listening")
    )
    assert question is None
    assert build_arabic_quiz(user) if kind == "arabic" else build_library_quiz(user)


@pytest.mark.parametrize("kind", ["arabic", "library"])
def test_listening_answers_idempotent_owned_and_extra_does_not_postpone_review(user, pool, kind):
    build = build_arabic_quiz if kind == "arabic" else build_library_quiz
    answer = answer_arabic_quiz if kind == "arabic" else answer_library_quiz
    question = build(user, mode="listening", extra_practice=True)
    progress = next(
        row
        for row, _ in pool[kind]
        if (
            row.item_id == question.target_item_id
            if kind == "arabic"
            else row.id == question.target_progress_id
        )
    )
    before = (progress.review_stage, progress.next_review_at)
    assert answer(question.id, user, question.correct_option)[1]
    assert not answer(question.id, user, 0)[1]
    progress.refresh_from_db()
    assert progress.total_answers == progress.correct_answers == 1
    assert (progress.review_stage, progress.next_review_at) == before
    other = TelegramUser.objects.create(telegram_id=998, first_name="Other")
    with pytest.raises((ArabicQuizQuestion.DoesNotExist, LibraryQuizQuestion.DoesNotExist)):
        answer(question.id, other, question.correct_option)


def test_targeted_reader_quiz_rejects_unstudied_content_and_keeps_studied_distractors(user, pool):
    target = pool["library"][2][0]
    question = build_library_quiz(user, mode="listening", item_id=target.passage_id)
    assert question.target_progress_id == target.id
    unstudiied = QuranPassage.objects.get(slug="audio-passage-4")
    with pytest.raises(ValueError, match="Study"):
        build_library_quiz(user, mode="listening", item_id=unstudiied.id)


@pytest.mark.parametrize("kind", ["arabic", "library"])
def test_identical_recordings_do_not_count_as_four_eligible_listening_candidates(user, pool, kind):
    first, second = pool[kind][0][1], pool[kind][1][1]
    second.url = first.url
    second.save(update_fields=["url"])
    question = (
        build_arabic_quiz(user, mode="listening")
        if kind == "arabic"
        else build_library_quiz(user, mode="listening")
    )
    assert question is None


def test_listening_api_mutations_require_csrf_and_reject_invalid_mode(user, pool):
    user.auth_user = get_user_model().objects.create_user(username="listening-owner")
    user.save(update_fields=["auth_user"])
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user.auth_user)
    for route in ("arabic", "library"):
        assert (
            client.post(f"/api/v1/{route}/quiz/", {"mode": "listening"}, format="json").status_code
            == 403
        )
    client.get("/api/v1/auth/session/")
    client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
    for route in ("arabic", "library"):
        assert (
            client.post(f"/api/v1/{route}/quiz/", {"mode": "invalid"}, format="json").status_code
            == 400
        )
        response = client.post(f"/api/v1/{route}/quiz/", {"mode": "listening"}, format="json")
        assert response.status_code == 200 and response.json()["question"]["audio_tracks"]
