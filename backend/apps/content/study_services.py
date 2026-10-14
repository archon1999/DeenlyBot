"""Read-only, language-aware linguistic sidecars. These are not generated tafsir."""

import re

from django.db.models import F

from .models import QuranPassage, QuranPassageAnalysis, QuranVerse
from .provenance import content_provenance


def resolve_library_reference(reference):
    parsed = re.fullmatch(r"(\d{1,3}):(\d{1,3})(?:[-–](\d{1,3}))?", reference or "")
    if not parsed:
        return None
    first, last = int(parsed[2]), int(parsed[3] or parsed[2])
    if not 1 <= first <= last:
        return None
    passage = (
        QuranPassage.objects.filter(
            is_published=True,
            surah_number=int(parsed[1]),
            ayah_start__lte=first,
            ayah_end__gte=last,
        )
        .annotate(span=F("ayah_end") - F("ayah_start"))
        .order_by("span", "id")
        .first()
    )
    return {"id": passage.id, "kind": passage.passage_type} if passage else None


def passage_contains_reference(reference, query):
    """A lesson about 1:5 links to the stored full 1:1–7 surah, not a duplicate."""
    pattern = r"(\d{1,3}):(\d{1,3})(?:[-–](\d{1,3}))?"
    passage = re.fullmatch(pattern, reference)
    requested = re.fullmatch(pattern, query)
    if not passage or not requested:
        return False
    first, last = int(passage[2]), int(passage[3] or passage[2])
    requested_first, requested_last = int(requested[2]), int(requested[3] or requested[2])
    return passage[1] == requested[1] and first <= requested_first <= requested_last <= last


def _localized(manager, language):
    return next((row for row in manager.all() if row.language == language), None)


def passage_analysis(passage, language):
    analysis = (
        QuranPassageAnalysis.objects.filter(
            passage=passage, is_verified=True, source__is_verified=True
        )
        .prefetch_related("translations")
        .select_related("source")
        .first()
    )
    if analysis is None:
        return None
    text = _localized(analysis.translations, language)
    if text is None:
        return None
    verses = QuranVerse.objects.filter(
        surah_number=passage.surah_number,
        ayah_number__gte=passage.ayah_start,
        ayah_number__lte=passage.ayah_end,
    ).prefetch_related("translations", "words__translations")
    result = []
    for verse in verses:
        verse_text = _localized(verse.translations, language)
        if verse_text is None:
            continue
        words = []
        for word in verse.words.all():
            word_text = _localized(word.translations, language)
            if word_text is not None:
                words.append(
                    {
                        "id": word.id,
                        "arabic_text": word.arabic_text,
                        "root": word.root,
                        "meaning": word_text.meaning,
                        "transcription": word_text.transcription,
                        "grammar_note": word_text.grammar_note,
                    }
                )
        result.append(
            {
                "key": verse.key,
                "arabic_text": verse.arabic_text,
                "translation": verse_text.translation,
                "transcription": verse_text.transcription,
                "words": words,
            }
        )
    if len(result) != passage.ayah_end - passage.ayah_start + 1:
        return None
    return {
        "provenance": content_provenance(analysis, "analysis"),
        "summary": text.summary,
        "context": text.context,
        "explanation": text.explanation,
        "verses": result,
    }
