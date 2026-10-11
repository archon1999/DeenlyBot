"""Refresh short-lived API metadata; never download or redistribute recordings."""

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.content.models import QuranPassage, QuranVerse, ReligiousSource

from .models import AudioAsset, AudioBinding
from .quran_foundation import QuranFoundationClient, QuranFoundationError, normalize_qf_audio_url
from .services import normalize_arabic


def _upsert(key, url, source, voice):
    now = timezone.now()
    asset, _ = AudioAsset.objects.update_or_create(
        key=key,
        defaults={
            "url": normalize_qf_audio_url(url),
            "file": "",
            "voice": voice,
            "source": source,
            "attribution": f"{voice} · Quran data provided by Quran Foundation",
            "license_notes": "Streaming through approved Quran Foundation Content APIs; "
            "recordings are not downloaded. Metadata expires within seven days.",
            "rights_confirmed": True,
            "pronunciation_verified": True,
            "is_published": True,
            "available": True,
            "provider": "quran_foundation",
            "checked_at": now,
            "expires_at": now + timedelta(days=6),
        },
    )
    asset.full_clean()
    return asset


def sync_verse_audio(client, verse, source):
    """Network work finishes before starting the short SQLite write transaction."""
    reference = f"{verse.surah_number}:{verse.ayah_number}"
    audio_response = client.verse_audio(reference)
    files = audio_response.get("audio_files", [])
    matching = [item for item in files if item.get("verse_key") == reference]
    if len(matching) != 1:
        raise QuranFoundationError("No unambiguous recording for the requested ayah.")
    url = normalize_qf_audio_url(matching[0].get("url"))
    words_response = client.verse_words(reference)
    remote_words = words_response.get("verse", {}).get("words", [])
    local_words = {word.position: word for word in verse.words.all()}
    valid_words = []
    for word in remote_words:
        position = word.get("position")
        local = local_words.get(position)
        if (
            local
            and word.get("audio_url")
            and normalize_arabic(word.get("text_uthmani", ""))
            == normalize_arabic(local.arabic_text)
        ):
            valid_words.append((local, normalize_qf_audio_url(word["audio_url"])))
    with transaction.atomic():
        asset = _upsert(
            f"qf:{settings.QF_ENV}:verse:{settings.QF_RECITATION_ID}:{reference}",
            url,
            source,
            settings.QF_RECITER_NAME,
        )
        AudioBinding.objects.get_or_create(
            asset=asset,
            verse=verse,
            defaults={"label": {language: reference for language in ("uz", "ru", "en")}},
        )
        for word, word_url in valid_words:
            word_asset = _upsert(
                f"qf:{settings.QF_ENV}:word:{reference}:{word.position}",
                word_url,
                source,
                "Quran Foundation word pronunciation",
            )
            AudioBinding.objects.get_or_create(
                asset=word_asset,
                word=word,
                defaults={"label": {language: word.arabic_text for language in ("uz", "ru", "en")}},
            )
    return 1 + len(valid_words)


def refresh_quran_audio(*, limit=8):
    client = QuranFoundationClient()
    source, _ = ReligiousSource.objects.get_or_create(
        title="Quran Foundation audio",
        defaults={
            "url": "https://quran.com",
            "is_verified": True,
            "notes": "Approved Quran Foundation Content API streaming. "
            "https://api-docs.quran.com/legal/developer-terms/",
        },
    )
    references = set()
    for passage in QuranPassage.objects.filter(is_published=True):
        references.update(
            (passage.surah_number, number)
            for number in range(passage.ayah_start, passage.ayah_end + 1)
        )
    verses = [
        verse
        for verse in QuranVerse.objects.prefetch_related("words").all()
        if (verse.surah_number, verse.ayah_number) in references
        and (settings.QF_ENV != "prelive" or verse.surah_number in (1, 2))
    ]
    existing = {
        binding.verse_id: binding.asset.checked_at
        for binding in AudioBinding.objects.filter(
            verse__isnull=False,
            asset__provider="quran_foundation",
            asset__key__startswith=f"qf:{settings.QF_ENV}:verse:{settings.QF_RECITATION_ID}:",
        ).select_related("asset")
    }
    old = timezone.now() - timedelta(days=5)
    verses = sorted(
        [verse for verse in verses if not existing.get(verse.id) or existing[verse.id] < old],
        key=lambda verse: (
            existing.get(verse.id) is not None,
            existing.get(verse.id) or old,
            verse.surah_number,
            verse.ayah_number,
        ),
    )[:limit]
    imported = 0
    failed = []
    for verse in verses:
        try:
            imported += sync_verse_audio(client, verse, source)
        except QuranFoundationError as error:
            failed.append(
                {"reference": f"{verse.surah_number}:{verse.ayah_number}", "error": str(error)}
            )
    return {"recordings": imported, "requested_verses": len(verses), "failed": failed}
