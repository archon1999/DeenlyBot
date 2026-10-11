from types import SimpleNamespace

import pytest
from django.core.management import call_command

from apps.arabic_learning.models import ArabicLesson, ArabicLessonCategory
from apps.arabic_learning.services import complete_lesson, lesson_with_content
from apps.telegram_bot.arabic_handlers import (
    _category_keyboard,
    _category_page,
    _dashboard_text,
)
from apps.telegram_bot.arabic_rendering import render_arabic_lesson


@pytest.fixture
def seeded_arabic(db):
    call_command("seed_arabic", verbosity=0)


@pytest.mark.django_db
def test_arabic_dashboard_and_category_pagination_do_not_create_progress(user, seeded_arabic):
    text = _dashboard_text(user)
    items, page, pages = _category_page(user, ArabicLessonCategory.ALPHABET, 1)
    keyboard = _category_keyboard("ru", ArabicLessonCategory.ALPHABET, items, page, pages)

    assert "0/62" in text
    assert (len(items), page, pages) == (10, 1, 2)
    assert keyboard.inline_keyboard[0][0].callback_data == "arabic:next:alphabet:1"
    assert keyboard.inline_keyboard[-2][-1].callback_data == "arabic:category:alphabet:2"
    assert user.arabic_lesson_progress.count() == 0
    assert user.arabic_item_progress.count() == 0


@pytest.mark.django_db
def test_completed_lesson_is_marked_and_all_lesson_messages_fit_telegram(user, seeded_arabic):
    first = ArabicLesson.objects.get(category=ArabicLessonCategory.ALPHABET, order=1)
    complete_lesson(user, first.id)
    items, _, _ = _category_page(user, ArabicLessonCategory.ALPHABET, 1)
    assert items[0][1].startswith("✅")

    for language in ("ru", "en", "uz"):
        display_user = SimpleNamespace(language=language)
        for lesson_id in ArabicLesson.objects.values_list("id", flat=True):
            rendered = render_arabic_lesson(display_user, lesson_with_content(lesson_id))
            assert 1 <= len(rendered) <= 4096
            assert "corpus.quran.com" not in rendered
            assert "Quran-focused Arabic learning curriculum" not in rendered
