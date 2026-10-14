from io import StringIO
from types import SimpleNamespace

import pytest
from django.core.management import call_command

from apps.api.dto import lesson_dto, library_dto, name_dto
from apps.arabic_learning.models import ArabicLesson
from apps.content.models import Dua, NameOfAllah, QuranPassage
from apps.content.provenance import public_source_url, reference_url
from apps.content.study_services import passage_analysis


@pytest.mark.parametrize("url", ["javascript:alert(1)", "data:text/html,test", "//example.org", "https://user:password@example.org", "https://[broken"])
def test_source_urls_do_not_allow_executable_or_credential_links(url):
    assert public_source_url(url) == ""


def test_reference_urls_are_resolved_from_recorded_numbers_only():
    assert reference_url("Quran 17:24") == "https://quran.com/17/24"
    assert reference_url("Abu Dawud 5088; at-Tirmidhi 3388") == "https://sunnah.com/abudawud:5088"
    assert reference_url("Сахих Муслим 2697 / Sahih Muslim 2697") == "https://sunnah.com/muslim:2697"
    assert reference_url("Quran 999:1") == ""
    assert reference_url("A general collection") == ""


@pytest.mark.django_db
def test_seeded_readers_expose_provenance_without_changing_materials_or_progress(user):
    call_command("seed_content", stdout=StringIO())
    call_command("seed_arabic", stdout=StringIO())
    call_command("seed_study", stdout=StringIO())
    for language in ("uz", "ru", "en"):
        profile = SimpleNamespace(id=user.id, pk=user.pk, language=language)
        # Provide the real profile where ORM ownership lookups are required.
        user.language = language
        for item in QuranPassage.objects.select_related("source").prefetch_related("translations"):
            before = (item.arabic_text, item.updated_at)
            result = library_dto(item, item.passage_type, user, favorite_ids=set())
            assert result["provenance"]["url"] == f"https://quran.com/{item.surah_number}/{item.ayah_start}"
            assert result["provenance"]["reference"] == result["reference"]
            if item.slug == "ayat-al-kursi":
                assert result["provenance"]["meaning_is_summary"]
            item.refresh_from_db()
            assert before == (item.arabic_text, item.updated_at)
        for item in Dua.objects.select_related("source").prefetch_related("translations"):
            result = library_dto(item, "dua", user, favorite_ids=set())
            assert result["provenance"]["reference"]
            assert result["provenance"]["url"].startswith(("https://sunnah.com/", "https://quran.com/"))
            assert result["provenance"]["url"] not in ("https://sunnah.com", "https://quran.com")
        name = NameOfAllah.objects.select_related("source").first()
        assert name_dto(name, profile)["provenance"]["kind"] == "name"
        lesson = ArabicLesson.objects.select_related("source").first()
        assert lesson_dto(lesson, profile, detail=True)["provenance"]["kind"] == "lesson"
        analysis = passage_analysis(QuranPassage.objects.get(slug="al-ikhlas"), language)
        assert analysis["provenance"]["kind"] == "analysis"
        assert analysis["provenance"]["url"].startswith("https://corpus.quran.com/")
