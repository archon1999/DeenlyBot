"""Read-only provenance, kept separate from learning meanings and audio credits.

A stored reference is not an endorsement of the locally written explanation.
Never infer scholarly certification from ReligiousSource.is_verified.
"""

import re
from urllib.parse import urlsplit


def public_source_url(value):
    try:
        parsed = urlsplit(value or "")
        if parsed.scheme in {"https", "http"} and parsed.hostname and not parsed.username:
            return value
    except ValueError:
        pass
    return ""


def reference_url(reference):
    """Resolve only explicitly recorded book/verse numbers, never a guessed citation."""
    quran = re.search(r"(?:Quran|Qur’an|Коран)\s+(\d{1,3}):(\d{1,3})", reference)
    if quran and 1 <= int(quran[1]) <= 114 and 1 <= int(quran[2]) <= 286:
        return f"https://quran.com/{quran[1]}/{quran[2]}"
    for name, collection in (
        (r"(?:al-)?Bukhari", "bukhari"),
        (r"Muslim", "muslim"),
        (r"Abu Dawud", "abudawud"),
        (r"(?:at-)?Tirmidhi", "tirmidhi"),
        (r"Ibn Majah", "ibnmajah"),
    ):
        match = re.search(rf"{name}\s+(\d+[a-z]?)\b", reference, re.IGNORECASE)
        if match:
            return f"https://sunnah.com/{collection}:{match[1]}"
    return ""


def content_provenance(item, kind, text=None):
    source = item.source
    reference = ""
    url = public_source_url(source.url)
    if kind in {"ayah", "surah"}:
        end = f"–{item.ayah_end}" if item.ayah_end != item.ayah_start else ""
        reference = f"{item.surah_number}:{item.ayah_start}{end}"
        url = f"https://quran.com/{item.surah_number}/{item.ayah_start}"
    elif kind == "dua" and text:
        reference = text.note.strip()
        url = reference_url(reference) or url
    meaning = getattr(text, "translation", "")
    return {
        "kind": kind,
        "title": source.title,
        "url": url,
        "reference": reference,
        "meaning_is_summary": "…" in meaning or "..." in meaning,
    }
