import asyncio

import pytest
from django.core.management import call_command

from apps.content.models import (
    Dua,
    Favorite,
    NameOfAllah,
    NameTranslation,
    QuranPassage,
    QuranPassageType,
)
from apps.content.services import localized_name, toggle_dua_favorite, toggle_passage_favorite
from apps.islamic_calendar.models import IslamicEvent
from apps.telegram_bot.handlers import _dua_list, _library_page_keyboard, _passage_list
from apps.telegram_bot.rendering import render_name_card


@pytest.mark.django_db
def test_seed_is_complete_multilingual_and_idempotent():
    call_command("seed_content", verbosity=0)
    call_command("seed_content", verbosity=0)
    assert NameOfAllah.objects.count() == 100
    assert NameTranslation.objects.count() == 100 * 3
    assert QuranPassage.objects.count() == 21
    assert Dua.objects.count() == 27
    assert IslamicEvent.objects.count() >= 7
    assert list(NameOfAllah.objects.values_list("order", flat=True)) == list(range(1, 101))
    assert list(NameOfAllah.objects.values_list("transliteration", flat=True)[:2]) == [
        "Allah",
        "Ar-Rahman",
    ]
    assert NameTranslation.objects.get(name__order=4, language="ru").transcription.startswith(
        "Аль-"
    )
    assert not NameTranslation.objects.filter(description__startswith="Это имя указывает").exists()
    assert not NameTranslation.objects.filter(transcription="").exists()
    assert not QuranPassage.objects.filter(translations__transcription="").exists()
    assert QuranPassage.objects.filter(passage_type=QuranPassageType.SURAH).count() == 10
    assert QuranPassage.objects.filter(passage_type=QuranPassageType.AYAH).count() == 11


@pytest.mark.django_db
def test_quran_and_dua_library_pages_have_ten_items():
    call_command("seed_content", verbosity=0)

    ayah_first, ayah_page, ayah_pages = _passage_list("ru", 1, QuranPassageType.AYAH)
    ayah_second, _, _ = _passage_list("ru", 2, QuranPassageType.AYAH)
    surahs, surah_page, surah_pages = _passage_list("ru", 1, QuranPassageType.SURAH)
    dua_first, dua_page, dua_pages = _dua_list("ru", 1)
    dua_second, _, _ = _dua_list("ru", 2)

    assert (len(ayah_first), len(ayah_second), ayah_page, ayah_pages) == (10, 1, 1, 2)
    assert (len(surahs), surah_page, surah_pages) == (10, 1, 1)
    assert (len(dua_first), len(dua_second), dua_page, dua_pages) == (10, 10, 1, 3)


def test_library_pagination_callbacks_target_registered_sections():
    quran_keyboard = _library_page_keyboard("ru", [(1, "Аят")], 1, 2, "passage")
    dua_keyboard = _library_page_keyboard("ru", [(1, "Дуа")], 1, 2, "dua")

    assert quran_keyboard.inline_keyboard[0][0].callback_data == "passage:1:ayah:1"
    assert quran_keyboard.inline_keyboard[-2][-1].callback_data == "library:quran:ayah:2"
    assert dua_keyboard.inline_keyboard[-2][-1].callback_data == "library:duas:2"


@pytest.mark.django_db
def test_prefetched_name_translation_is_safe_inside_async_context(user, four_names):
    name = (
        NameOfAllah.objects.select_related("source")
        .prefetch_related("translations")
        .get(id=four_names[0].id)
    )

    async def render_without_database_access():
        translation = localized_name(name, user.language).meaning
        return translation, render_name_card(user, name)

    meaning, card = asyncio.run(render_without_database_access())
    assert meaning == "Meaning 1 ru"
    assert "Name 1" in card
    assert "Test source" not in card


@pytest.mark.django_db
def test_favorites_toggle_without_duplicates(user, source):
    passage = QuranPassage.objects.create(
        slug="test",
        surah_number=1,
        ayah_start=1,
        ayah_end=1,
        arabic_text="test",
        source=source,
    )
    assert toggle_passage_favorite(user, passage) is True
    assert toggle_passage_favorite(user, passage) is False
    assert Favorite.objects.count() == 0

    dua = Dua.objects.create(slug="test-dua", source=source)
    assert toggle_dua_favorite(user, dua) is True
    assert Favorite.objects.get().dua == dua
