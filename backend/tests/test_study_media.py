import io
import json
from datetime import timedelta
from unittest.mock import patch
from urllib.error import HTTPError

import pytest
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone

from apps.content.models import QuranPassage, QuranVerse, QuranWord
from apps.study_media.models import AudioAsset, AudioBinding, validate_audio_url
from apps.study_media.quran_foundation import (
    QuranFoundationClient,
    QuranFoundationError,
    normalize_qf_audio_url,
)
from apps.study_media.services import audio_tracks_for, normalize_arabic


@pytest.fixture
def audio_asset(source):
    return AudioAsset.objects.create(
        key="verified-recording",
        url="https://upload.wikimedia.org/test.ogg",
        voice="Native speaker",
        source=source,
        attribution="Speaker · CC-BY-SA 4.0",
        license_notes="CC-BY-SA 4.0",
        rights_confirmed=True,
        pronunciation_verified=True,
        is_published=True,
        available=True,
    )


@pytest.mark.django_db
def test_audio_playback_requires_rights_review_availability_and_not_expired(
    audio_asset, four_names
):
    name = four_names[0]
    AudioBinding.objects.create(asset=audio_asset, name=name, label={"uz": "Talaffuz"})
    assert audio_tracks_for("name", name, "uz")[0]["label"] == "Talaffuz"
    for field in ("rights_confirmed", "pronunciation_verified", "available", "is_published"):
        setattr(audio_asset, field, False)
        audio_asset.save()
        assert audio_tracks_for("name", name) == []
        setattr(audio_asset, field, True)
    audio_asset.expires_at = timezone.now() - timedelta(seconds=1)
    audio_asset.save()
    assert audio_tracks_for("name", name) == []


@pytest.mark.django_db
def test_published_audio_cannot_skip_license_review(audio_asset):
    audio_asset.rights_confirmed = False
    with pytest.raises(ValidationError):
        audio_asset.full_clean()


@pytest.mark.django_db
def test_audio_binding_database_requires_exactly_one_target(audio_asset, four_names):
    with pytest.raises(IntegrityError), transaction.atomic():
        AudioBinding.objects.create(asset=audio_asset)
    AudioBinding.objects.create(asset=audio_asset, name=four_names[0])
    with pytest.raises(IntegrityError), transaction.atomic():
        AudioBinding.objects.create(asset=audio_asset, name=four_names[0])


@pytest.mark.django_db
def test_passage_playlist_is_not_offered_when_an_ayah_is_missing(audio_asset, source):
    passage = QuranPassage.objects.create(
        slug="test",
        surah_number=1,
        ayah_start=1,
        ayah_end=2,
        arabic_text="بِسْمِ اللَّهِ الْحَمْدُ لِلَّهِ",
        source=source,
    )
    verse = QuranVerse.objects.create(
        surah_number=1, ayah_number=1, arabic_text="بِسْمِ اللَّهِ", source=source
    )
    AudioBinding.objects.create(asset=audio_asset, verse=verse)
    assert audio_tracks_for("surah", passage) == []
    verse2 = QuranVerse.objects.create(
        surah_number=1, ayah_number=2, arabic_text="الْحَمْدُ لِلَّهِ", source=source
    )
    AudioBinding.objects.create(asset=audio_asset, verse=verse2)
    assert len(audio_tracks_for("surah", passage)) == 2


@pytest.mark.django_db
def test_name_can_use_exact_quran_word_audio_but_not_prefixed_word(audio_asset, source):
    from apps.content.models import NameOfAllah

    verse = QuranVerse.objects.create(
        surah_number=1, ayah_number=3, arabic_text="الرَّحْمَٰنِ", source=source
    )
    word = QuranWord.objects.create(verse=verse, position=1, arabic_text="ٱلرَّحْمَٰنِ")
    AudioBinding.objects.create(asset=audio_asset, word=word)
    name = NameOfAllah.objects.create(
        order=1, arabic="الرَّحْمَن", transliteration="Ar-Rahman", source=source
    )
    assert len(audio_tracks_for("name", name)) == 1
    name.arabic = "رَحْمَن"
    assert audio_tracks_for("name", name) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/test.mp3",
        "https://localhost/test.mp3",
        "https://127.0.0.1/test.mp3",
        "https://user:pass@example.com/test.mp3",
        "https://192.168.1.1/test.mp3",
        "data:audio/mp3,test",
        "https://audio.internal/test.mp3",
    ],
)
def test_only_public_https_recording_urls(url):
    with pytest.raises(ValidationError):
        validate_audio_url(url)


def test_quran_url_normalization_is_bounded_to_expected_hosts():
    assert normalize_qf_audio_url("wbw/001_002_001.mp3").startswith("https://audio.qurancdn.com/")
    assert normalize_qf_audio_url("Alafasy/mp3/001002.mp3").startswith("https://verses.quran.com/")
    with pytest.raises(QuranFoundationError):
        normalize_qf_audio_url("https://unexpected.example/file.mp3")
    assert normalize_arabic("ٱلرَّحْمَٰنِ") == normalize_arabic("الرَّحْمَن")
    assert normalize_arabic("الْحَمْدُ ۝ لِلَّهِ") == normalize_arabic("الْحَمْدُ لِلَّهِ")


def _response(data):
    return io.BytesIO(json.dumps(data).encode())


@override_settings(QF_CLIENT_ID="test-client", QF_CLIENT_SECRET="test-secret", QF_ENV="prelive")
def test_qf_token_is_cached_and_never_sent_in_query():
    cache.clear()
    with patch(
        "apps.study_media.quran_foundation.urlopen",
        side_effect=[
            _response({"access_token": "test-token", "expires_in": 3600}),
            _response({"chapters": []}),
            _response({"chapters": []}),
        ],
    ) as request:
        client = QuranFoundationClient()
        client.get("/chapters")
        client.get("/chapters")
    assert request.call_count == 3
    token_request = request.call_args_list[0].args[0]
    assert token_request.data == b"grant_type=client_credentials&scope=content"
    assert "test-secret" not in token_request.full_url
    api_request = request.call_args_list[1].args[0]
    assert api_request.get_header("X-auth-token") == "test-token"
    assert api_request.get_header("User-agent").startswith("Deenly/")


@override_settings(QF_CLIENT_ID="test-client", QF_CLIENT_SECRET="test-secret", QF_ENV="prelive")
def test_qf_retries_401_exactly_once_without_leaking_response_body():
    cache.clear()
    rejected = HTTPError("https://example.test", 401, "Rejected", {}, None)
    with patch(
        "apps.study_media.quran_foundation.urlopen",
        side_effect=[
            _response({"access_token": "first-token"}),
            rejected,
            _response({"access_token": "second-token"}),
            _response({"ok": True}),
        ],
    ) as request:
        assert QuranFoundationClient().get("/chapters") == {"ok": True}
    assert request.call_count == 4


@override_settings(QF_CLIENT_ID="", QF_CLIENT_SECRET="", QF_ENV="prelive")
def test_missing_qf_credentials_fails_without_network_call():
    with patch("apps.study_media.quran_foundation.urlopen") as request:
        with pytest.raises(QuranFoundationError, match="not configured"):
            QuranFoundationClient()
    request.assert_not_called()
