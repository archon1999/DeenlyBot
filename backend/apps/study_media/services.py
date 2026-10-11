import re
import unicodedata

from django.db.models import Q
from django.utils import timezone

from .models import AudioBinding


def normalize_arabic(text):
    return "".join(
        character
        for character in unicodedata.normalize("NFKC", text or "")
        if not unicodedata.category(character).startswith("M")
        and character not in {"ـ", "۝", "۞", "۩"}
        and not character.isspace()
        and character not in "،؛.!؟"
    ).replace("ٱ", "ا")


def _ready_bindings(**lookup):
    return (
        AudioBinding.objects.filter(
            **lookup,
            asset__is_published=True,
            asset__available=True,
            asset__rights_confirmed=True,
            asset__pronunciation_verified=True,
        )
        .filter(Q(asset__expires_at__isnull=True) | Q(asset__expires_at__gt=timezone.now()))
        .select_related("asset", "asset__source")
    )


def _dto(binding, language, fallback="Audio"):
    asset = binding.asset
    return {
        "id": str(asset.id),
        "label": binding.label.get(language) or binding.label.get("en") or fallback,
        "voice": asset.voice,
        "url": asset.url or asset.file.url,
        "duration_ms": asset.duration_ms,
        "segments": asset.segments,
        "attribution": asset.attribution,
        "source_url": asset.source.url,
    }


def _verse_audio(surah, first, last, language, *, expected_arabic=None):
    if expected_arabic is not None:
        from apps.content.models import QuranVerse

        verses = list(
            QuranVerse.objects.filter(
                surah_number=surah, ayah_number__gte=first, ayah_number__lte=last
            ).order_by("ayah_number")
        )
        if len(verses) != last - first + 1 or normalize_arabic(expected_arabic) != normalize_arabic(
            " ".join(verse.arabic_text for verse in verses)
        ):
            return []
    bindings = (
        _ready_bindings(
            verse__surah_number=surah,
            verse__ayah_number__gte=first,
            verse__ayah_number__lte=last,
        )
        .select_related("verse")
        .order_by("verse__ayah_number", "order", "id")
    )
    tracks = []
    seen_verses = set()
    for binding in bindings:
        if binding.verse_id not in seen_verses:
            tracks.append(_dto(binding, language, f"{surah}:{binding.verse.ayah_number}"))
            seen_verses.add(binding.verse_id)
    # Do not imply that an incomplete recording covers the whole passage.
    return tracks if len(seen_verses) == last - first + 1 else []


def audio_tracks_for(kind, item, language="uz"):
    target = {
        "name": "name",
        "ayah": "passage",
        "surah": "passage",
        "dua": "dua",
        "arabic": "arabic_item",
        "word": "word",
    }.get(kind)
    if target is None or item is None:
        return []
    direct = list(_ready_bindings(**{target: item}))
    if kind in {"ayah", "surah"}:
        return [
            *[_dto(binding, language) for binding in direct],
            *_verse_audio(
                item.surah_number,
                item.ayah_start,
                item.ayah_end,
                language,
                expected_arabic=item.arabic_text,
            ),
        ]
    if direct:
        return [_dto(binding, language) for binding in direct]
    if kind == "arabic":
        reference = re.fullmatch(
            r"(\d{1,3}):(\d{1,3})(?:[-–](\d{1,3}))?", item.quran_reference or ""
        )
        if reference and item.metadata.get("audio_scope") == "verse":
            surah, first, last = (
                int(reference[1]),
                int(reference[2]),
                int(reference[3] or reference[2]),
            )
            return _verse_audio(surah, first, last, language, expected_arabic=item.arabic_text)
        if reference and item.metadata.get("audio_scope") == "words":
            from apps.content.models import QuranWord

            start = item.metadata.get("audio_word_from")
            end = item.metadata.get("audio_word_to")
            if not (isinstance(start, int) and isinstance(end, int) and 1 <= start <= end):
                return []
            words = list(
                QuranWord.objects.filter(
                    verse__surah_number=int(reference[1]),
                    verse__ayah_number=int(reference[2]),
                    position__gte=start,
                    position__lte=end,
                ).order_by("position")
            )
            if len(words) != end - start + 1 or normalize_arabic(
                item.arabic_text
            ) != normalize_arabic(" ".join(word.arabic_text for word in words)):
                return []
            tracks = []
            for word in words:
                binding = _ready_bindings(word=word).first()
                if binding is None:
                    return []
                tracks.append(_dto(binding, language))
            return tracks
        # A word recording must match the whole card, not merely contain it.
        from apps.content.models import QuranWord

        word_ids = [
            word.id
            for word in QuranWord.objects.all().only("id", "arabic_text")
            if normalize_arabic(word.arabic_text) == normalize_arabic(item.arabic_text)
        ]
        bindings = _ready_bindings(word_id__in=word_ids)
        first_binding = bindings.first()
        return [_dto(first_binding, language)] if first_binding else []
    if kind == "name":
        from apps.content.models import QuranWord

        word_ids = [
            word.id
            for word in QuranWord.objects.all().only("id", "arabic_text")
            if normalize_arabic(word.arabic_text) == normalize_arabic(item.arabic)
        ]
        binding = _ready_bindings(word_id__in=word_ids).first()
        return [_dto(binding, language)] if binding else []
    return []


def eligible_audio_for(kind, item, language="uz"):
    """Published reviewed recordings only; never fetch the network during a quiz."""
    return audio_tracks_for(kind, item, language)
