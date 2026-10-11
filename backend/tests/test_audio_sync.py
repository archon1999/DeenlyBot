from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.test import override_settings
from django.utils import timezone

from apps.content.models import QuranPassage, QuranVerse, QuranWord
from apps.study_media.models import AudioAsset, AudioBinding
from apps.study_media.quran_foundation import QuranFoundationError
from apps.study_media.services import audio_tracks_for
from apps.study_media.sync import refresh_quran_audio, sync_verse_audio

pytestmark = pytest.mark.django_db


@pytest.fixture
def verse(source):
    result = QuranVerse.objects.create(
        surah_number=1, ayah_number=1, arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ", source=source
    )
    for position, text in enumerate(result.arabic_text.split(), 1):
        QuranWord.objects.create(verse=result, position=position, arabic_text=text)
    return result


@pytest.fixture
def remote():
    return SimpleNamespace(
        verse_audio=Mock(
            return_value={"audio_files": [{"verse_key": "1:1", "url": "Alafasy/mp3/001001.mp3"}]}
        ),
        verse_words=Mock(
            return_value={
                "verse": {
                    "words": [
                        {"position": 1, "text_uthmani": "بِسْمِ", "audio_url": "wbw/001_001_001.mp3"},
                        {"position": 2, "text_uthmani": "ٱللَّهِ", "audio_url": "wbw/001_001_002.mp3"},
                        {
                            "position": 3,
                            "text_uthmani": "ٱلرَّحْمَٰنِ",
                            "audio_url": "wbw/001_001_003.mp3",
                        },
                    ]
                }
            }
        ),
    )


@override_settings(QF_ENV="prelive", QF_RECITATION_ID=7, QF_RECITER_NAME="Reviewed reciter")
def test_sync_is_idempotent_uses_exact_binding_ids_and_refreshes_short_lived_metadata(
    verse, source, remote, monkeypatch
):
    now = timezone.now()
    monkeypatch.setattr("apps.study_media.sync.timezone.now", lambda: now)
    assert sync_verse_audio(remote, verse, source) == 4
    assets = dict(AudioAsset.objects.values_list("key", "id"))
    bindings = list(AudioBinding.objects.values_list("id", flat=True))
    assert len(assets) == len(bindings) == 4
    assert all(
        asset.expires_at == now + timedelta(days=6) and not asset.file and asset.can_play
        for asset in AudioAsset.objects.all()
    )
    assert all(
        asset.attribution and asset.rights_confirmed and asset.pronunciation_verified
        for asset in AudioAsset.objects.all()
    )
    later = now + timedelta(days=1)
    monkeypatch.setattr("apps.study_media.sync.timezone.now", lambda: later)
    assert sync_verse_audio(remote, verse, source) == 4
    assert dict(AudioAsset.objects.values_list("key", "id")) == assets
    assert list(AudioBinding.objects.values_list("id", flat=True)) == bindings
    assert all(
        asset.checked_at == later and asset.expires_at == later + timedelta(days=6)
        for asset in AudioAsset.objects.all()
    )
    remote.verse_audio.assert_called_with("1:1")
    remote.verse_words.assert_called_with("1:1")


def test_word_audio_requires_both_position_and_matching_normalized_arabic(verse, source, remote):
    remote.verse_words.return_value = {
        "verse": {
            "words": [
                {"position": 1, "text_uthmani": "ٱللَّهِ", "audio_url": "wbw/wrong-position.mp3"},
                {"position": 2, "text_uthmani": "ٱللَّهِ", "audio_url": "wbw/right-word.mp3"},
                {"position": 3, "text_uthmani": "الرَّحِيمِ", "audio_url": "wbw/wrong-text.mp3"},
                {"position": 4, "text_uthmani": "﴿١﴾", "audio_url": "wbw/verse-ending.mp3"},
            ]
        }
    }
    assert sync_verse_audio(remote, verse, source) == 2
    binding = AudioBinding.objects.get(word__isnull=False)
    assert binding.word.position == 2
    assert binding.asset.url == "https://audio.qurancdn.com/wbw/right-word.mp3"
    assert not AudioAsset.objects.filter(url__contains="wrong").exists()


@pytest.mark.parametrize(
    "files",
    [
        [],
        [{"verse_key": "1:2", "url": "other.mp3"}],
        [{"verse_key": "1:1", "url": "a.mp3"}, {"verse_key": "1:1", "url": "b.mp3"}],
    ],
)
def test_missing_or_ambiguous_requested_verse_never_creates_assets(verse, source, remote, files):
    remote.verse_audio.return_value = {"audio_files": files}
    with pytest.raises(QuranFoundationError, match="unambiguous"):
        sync_verse_audio(remote, verse, source)
    assert not AudioAsset.objects.exists() and not AudioBinding.objects.exists()
    remote.verse_words.assert_not_called()


def test_invalid_remote_word_url_rejects_entire_batch_before_any_database_write(
    verse, source, remote
):
    remote.verse_words.return_value["verse"]["words"][2]["audio_url"] = (
        "https://attacker.example/clip.mp3"
    )
    with pytest.raises(QuranFoundationError, match="unsupported audio host"):
        sync_verse_audio(remote, verse, source)
    assert not AudioAsset.objects.exists() and not AudioBinding.objects.exists()


def test_expired_metadata_disappears_from_playback_without_losing_binding_identity(
    verse, source, remote
):
    sync_verse_audio(remote, verse, source)
    passage = QuranPassage.objects.create(
        slug="sync-playback",
        surah_number=1,
        ayah_start=1,
        ayah_end=1,
        source=source,
        arabic_text=verse.arabic_text,
    )
    tracks = audio_tracks_for("ayah", passage)
    assert len(tracks) == 1
    original_id = tracks[0]["id"]
    AudioAsset.objects.filter(bindings__verse=verse).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    assert audio_tracks_for("ayah", passage) == []
    sync_verse_audio(remote, verse, source)
    assert audio_tracks_for("ayah", passage)[0]["id"] == original_id


def test_refresh_prioritizes_only_published_passages_and_skips_fresh_metadata(
    verse, source, remote, monkeypatch
):
    QuranPassage.objects.create(
        slug="active-sync",
        surah_number=1,
        ayah_start=1,
        ayah_end=1,
        source=source,
        arabic_text=verse.arabic_text,
    )
    other = QuranVerse.objects.create(
        surah_number=112, ayah_number=1, arabic_text="قُلْ هُوَ اللَّهُ أَحَدٌ", source=source
    )
    QuranPassage.objects.create(
        slug="inactive-sync",
        surah_number=112,
        ayah_start=1,
        ayah_end=1,
        source=source,
        arabic_text=other.arabic_text,
        is_published=False,
    )
    monkeypatch.setattr("apps.study_media.sync.QuranFoundationClient", lambda: remote)
    first = refresh_quran_audio(limit=1)
    assert first == {"recordings": 4, "requested_verses": 1, "failed": []}
    remote.verse_audio.reset_mock()
    assert refresh_quran_audio(limit=1) == {"recordings": 0, "requested_verses": 0, "failed": []}
    remote.verse_audio.assert_not_called()
    AudioAsset.objects.filter(bindings__verse=verse).update(
        checked_at=timezone.now() - timedelta(days=5, seconds=1)
    )
    assert refresh_quran_audio(limit=1)["requested_verses"] == 1
    assert not AudioBinding.objects.filter(verse=other).exists()
