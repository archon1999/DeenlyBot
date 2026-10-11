from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.arabic_learning.categories import categories_for_language
from apps.arabic_learning.models import (
    ArabicItemTranslation,
    ArabicLearningItem,
    ArabicLesson,
    ArabicLessonCategory,
    ArabicLessonTranslation,
    UserArabicItemProgress,
)
from apps.arabic_learning.seed_data import ARABIC_LESSONS
from apps.content.management.commands.seed_content import DUAS, PASSAGES
from apps.content.models import Dua, DuaTranslation, QuranPassage, QuranPassageTranslation
from apps.content.seed_duas import EXTRA_DUAS
from apps.content.seed_quran import SHORT_SURAH_SLUGS
from apps.telegram_bot.arabic_rendering import render_arabic_lesson
from apps.telegram_bot.keyboards import arabic_dashboard_keyboard


def seed(command):
    call_command(command, stdout=StringIO(), verbosity=0)


@pytest.mark.parametrize("language", ["uz", "ru", "en"])
def test_category_catalog_matches_models_and_bot(language):
    categories = categories_for_language(language)
    assert len(categories) == 7
    assert {row["key"] for row in categories} == set(ArabicLessonCategory.values)
    assert all(row["title"] and row["description"] for row in categories)
    callbacks = {
        button.callback_data
        for row in arabic_dashboard_keyboard(language).inline_keyboard
        for button in row
    }
    assert {f"arabic:category:{row['key']}:1" for row in categories} <= callbacks
    grammar = next(row for row in categories if row["key"] == "grammar")
    assert grammar["title"] == {"uz": "Nahv", "ru": "Нахв", "en": "Nahw"}[language]


def test_curriculum_contains_substantial_new_tracks_without_fake_audio():
    counts = {category: 0 for category in ArabicLessonCategory.values}
    assert len({row["slug"] for row in ARABIC_LESSONS}) == len(ARABIC_LESSONS)
    for row in ARABIC_LESSONS:
        counts[row["category"]] += 1
        assert row["items"]
        for item in row["items"]:
            assert not item.get("audio_url")
            assert all(item["translations"]["transcription"][lang] for lang in ("uz", "ru", "en"))
            assert all(item["translations"]["meaning"][lang] for lang in ("uz", "ru", "en"))
    assert counts == {
        "alphabet": 16,
        "quran_vocabulary": 12,
        "grammar": 10,
        "prayer_arabic": 8,
        "sarf": 6,
        "daily_phrases": 6,
        "listening": 4,
    }
    assert len(ARABIC_LESSONS) == 62
    assert sum(len(row["items"]) for row in ARABIC_LESSONS) == 184
    for row in ARABIC_LESSONS:
        if row["category"] == "listening":
            assert all(
                item["reference"] and item["metadata"]["audio_scope"] == "verse"
                for item in row["items"]
            )


@pytest.mark.django_db
def test_arabic_seed_is_additive_and_preserves_progress_and_custom_audio(user):
    seed("seed_arabic")
    original_ids = dict(ArabicLesson.objects.values_list("slug", "id"))
    original_items = dict(ArabicLearningItem.objects.values_list("id", "arabic_text"))
    lesson = ArabicLesson.objects.get(slug="alif-ba")
    existing = lesson.items.first()
    existing.audio_url = "https://example.org/reviewed-own-recording.mp3"
    existing.save(update_fields=["audio_url"])
    surplus = ArabicLearningItem.objects.create(
        lesson=lesson, order=99, item_type="word", arabic_text="مِثَالٌ"
    )
    now = timezone.now()
    progress = UserArabicItemProgress.objects.create(
        user=user,
        item=surplus,
        introduced_at=now,
        next_review_at=now,
        review_stage=3,
        correct_streak=2,
        total_answers=5,
        correct_answers=4,
    )
    preserved_progress = UserArabicItemProgress.objects.values().get(pk=progress.pk)
    custom = ArabicLesson.objects.create(
        slug="owner-custom-lesson",
        category="grammar",
        order=99,
        source=lesson.source,
        is_published=True,
    )
    seed("seed_arabic")
    seed("seed_arabic")
    assert (
        dict(ArabicLesson.objects.filter(slug__in=original_ids).values_list("slug", "id"))
        == original_ids
    )
    assert (
        dict(
            ArabicLearningItem.objects.filter(pk__in=original_items).values_list(
                "id", "arabic_text"
            )
        )
        == original_items
    )
    existing.refresh_from_db()
    custom.refresh_from_db()
    assert existing.audio_url == "https://example.org/reviewed-own-recording.mp3"
    assert custom.is_published is True
    assert ArabicLearningItem.objects.filter(pk=surplus.pk).exists()
    assert UserArabicItemProgress.objects.values().get(pk=progress.pk) == preserved_progress


@pytest.mark.django_db
def test_all_expanded_lessons_have_three_translations_and_fit_telegram(user):
    seed("seed_arabic")
    assert ArabicLessonTranslation.objects.count() == 62 * 3
    assert ArabicItemTranslation.objects.count() == 184 * 3
    lessons = ArabicLesson.objects.prefetch_related("translations", "items__translations")
    for language in ("uz", "ru", "en"):
        user.language = language
        for lesson in lessons:
            assert len(render_arabic_lesson(user, lesson)) < 4096


@pytest.mark.django_db
def test_library_seed_expands_without_changing_existing_ids():
    seed("seed_content")
    passage_ids = dict(QuranPassage.objects.values_list("slug", "pk"))
    dua_ids = dict(Dua.objects.values_list("slug", "pk"))
    assert len(passage_ids) == len(PASSAGES) == 21
    assert len(dua_ids) == len(DUAS) == 27
    assert (
        set(QuranPassage.objects.filter(passage_type="surah").values_list("slug", flat=True))
        == SHORT_SURAH_SLUGS
    )
    assert QuranPassageTranslation.objects.count() == 21 * 3
    assert DuaTranslation.objects.count() == 27 * 3
    assert not DuaTranslation.objects.filter(transcription="").exists()
    assert not QuranPassageTranslation.objects.filter(transcription="").exists()
    seed("seed_content")
    assert dict(QuranPassage.objects.values_list("slug", "pk")) == passage_ids
    assert dict(Dua.objects.values_list("slug", "pk")) == dua_ids


def test_new_duas_have_individual_sources_and_localized_transcriptions():
    new_rows = [row for row in EXTRA_DUAS if row.get("source_url")]
    assert len(new_rows) == 14
    assert len({row["slug"] for row in DUAS}) == len(DUAS)
    assert len({row["arabic"] for row in new_rows}) == len(new_rows)
    for row in new_rows:
        assert row["source_url"].startswith("https://sunnah.com/")
        assert row["source"]
        assert set(row["transcriptions"]) == {"ru", "en", "uz"}
        assert all(row["transcriptions"].values())
        assert not row.get("audio_url")
