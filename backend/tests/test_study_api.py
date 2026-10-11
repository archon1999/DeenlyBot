import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.content.models import (
    QuranAnalysisTranslation,
    QuranPassage,
    QuranPassageAnalysis,
    QuranPassageTranslation,
    QuranVerse,
    QuranWord,
    QuranWordTranslation,
)
from apps.content.study_seed import seed_study_content
from apps.content.study_services import passage_analysis, resolve_library_reference
from apps.library_learning.services import confirm_library_studied

pytestmark = pytest.mark.django_db
API = "/api/v1/"


@pytest.fixture
def study_content():
    call_command("seed_content", verbosity=0)
    before = list(QuranPassage.objects.values())
    result = seed_study_content()
    return before, result


@pytest.fixture
def client(user):
    user.auth_user = get_user_model().objects.create_user(username="study-owner")
    user.save(update_fields=["auth_user"])
    result = APIClient(enforce_csrf_checks=True)
    result.get(API + "auth/session/")
    result.defaults["HTTP_X_CSRFTOKEN"] = result.cookies["csrftoken"].value
    result.force_login(user.auth_user)
    return result


def test_seed_is_additive_canonical_localized_and_idempotent(study_content):
    before, result = study_content
    assert result == {"new_passages": 0, "verses": 48}
    assert (
        list(QuranPassage.objects.filter(id__in=[row["id"] for row in before]).values()) == before
    )
    assert QuranPassageAnalysis.objects.count() == 12
    assert QuranVerse.objects.count() == 48
    assert QuranAnalysisTranslation.objects.count() == 36
    assert all(
        QuranWordTranslation.objects.filter(word=word).count() == 3
        for word in QuranWord.objects.all()
    )
    ids = list(QuranVerse.objects.values_list("id", flat=True))
    assert seed_study_content() == {"new_passages": 0, "verses": 48}
    assert list(QuranVerse.objects.values_list("id", flat=True)) == ids
    verse = QuranVerse.objects.get(surah_number=21, ayah_number=87)
    assert verse.arabic_text.startswith("وَذَا النُّونِ")
    assert "لَا إِلَٰهَ" in verse.arabic_text
    assert QuranWord.objects.get(verse=verse, arabic_text="لَا").position == 15
    kursi = QuranVerse.objects.get(surah_number=2, ayah_number=255)
    assert QuranWord.objects.get(verse=kursi, arabic_text="يَعْلَمُ").position == 27


@pytest.mark.parametrize("language", ["uz", "ru", "en"])
def test_every_seeded_analysis_has_complete_verse_translation_and_real_selected_words(
    study_content, language
):
    for record in QuranPassageAnalysis.objects.select_related("passage"):
        analysis = passage_analysis(record.passage, language)
        assert analysis and analysis["summary"] and analysis["context"] and analysis["explanation"]
        assert len(analysis["verses"]) == record.passage.ayah_end - record.passage.ayah_start + 1
        for verse in analysis["verses"]:
            assert verse["translation"] and verse["transcription"] and verse["words"]
            assert all(
                word["arabic_text"] in verse["arabic_text"]
                and word["meaning"]
                and word["grammar_note"]
                for word in verse["words"]
            )


def test_unverified_or_missing_language_analysis_is_not_published(study_content):
    passage = QuranPassage.objects.get(slug="al-fatiha")
    record = passage.analysis
    record.is_verified = False
    record.save(update_fields=["is_verified"])
    assert passage_analysis(passage, "uz") is None
    record.is_verified = True
    record.save(update_fields=["is_verified"])
    record.source.is_verified = False
    record.source.save(update_fields=["is_verified"])
    assert passage_analysis(passage, "uz") is None


def test_seed_preserves_editor_changes_and_existing_passage_translation(study_content):
    passage = QuranPassage.objects.get(slug="al-fatiha")
    text = QuranPassageTranslation.objects.get(passage=passage, language="uz")
    text.translation = "Owner-reviewed custom text"
    text.save()
    analysis = QuranAnalysisTranslation.objects.get(analysis=passage.analysis, language="uz")
    analysis.explanation = "Editor-reviewed explanation"
    analysis.save()
    seed_study_content()
    text.refresh_from_db()
    analysis.refresh_from_db()
    assert text.translation == "Owner-reviewed custom text"
    assert analysis.explanation == "Editor-reviewed explanation"


def test_detail_requires_auth_has_owned_progress_and_does_not_leak_source_metadata(
    study_content, client, user
):
    passage = QuranPassage.objects.get(slug="al-fatiha")
    route = API + f"library/surah/{passage.id}/"
    assert APIClient().get(route).status_code == 403
    payload = client.get(route).json()
    assert payload["analysis"]["verses"][0]["key"] == "1:1"
    assert payload["audio_tracks"] == [] and not payload["is_studied"]
    assert "source" not in payload and "source_url" not in payload["analysis"]
    confirm_library_studied(user, "surah", passage.id)
    assert client.get(route).json()["is_studied"]
    assert client.get(API + f"library/ayah/{passage.id}/").status_code == 404
    passage.is_published = False
    passage.save(update_fields=["is_published"])
    assert client.get(route).status_code == 404


def test_lesson_reference_search_resolves_containing_surah_without_duplicate_passage(
    study_content, client
):
    fatiha = QuranPassage.objects.get(slug="al-fatiha")
    response = client.get(API + "library/?kind=surah&q=1:5").json()
    assert [row["id"] for row in response["results"]] == [fatiha.id]
    assert client.get(API + "library/?kind=surah&q=1:4-5").json()["count"] == 1
    assert client.get(API + "library/?kind=surah&q=1:8").json()["count"] == 0
    assert resolve_library_reference("1:5") == {"id": fatiha.id, "kind": "surah"}
    assert resolve_library_reference("1:4-5") == {"id": fatiha.id, "kind": "surah"}
    assert resolve_library_reference("1:8") is None
    assert resolve_library_reference("invalid") is None


@pytest.mark.parametrize("language", ["uz", "ru", "en"])
def test_overview_category_contract_and_dashboard_support_new_categories(client, user, language):
    call_command("seed_arabic", verbosity=0)
    user.language = language
    user.save(update_fields=["language"])
    response = client.get(API + "arabic/").json()
    assert [row["key"] for row in response["categories"]] == [
        "alphabet",
        "quran_vocabulary",
        "grammar",
        "prayer_arabic",
        "sarf",
        "daily_phrases",
        "listening",
    ]
    assert all(row["title"] and row["description"] for row in response["categories"])
    assert client.get(API + "dashboard/").status_code == 200
