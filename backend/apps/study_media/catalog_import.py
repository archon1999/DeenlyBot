"""Import recordings whose content identity and license are known, without downloads."""

from django.db import transaction
from django.utils import timezone

from apps.arabic_learning.models import ArabicLearningItem
from apps.content.models import Dua, NameOfAllah, QuranPassage, ReligiousSource

from .commons_catalog import COMMONS_AUDIO_CATALOG
from .models import AudioAsset, AudioBinding
from .services import normalize_arabic


def _targets(row):
    kind = row["target_kind"]
    if kind == "name":
        return [
            ("name", name)
            for name in NameOfAllah.objects.filter(
                transliteration=row["target_transliteration"], is_published=True
            )
        ]
    if kind == "surah":
        return [
            ("passage", passage)
            for passage in QuranPassage.objects.filter(
                passage_type="surah",
                surah_number=row["surah_number"],
                ayah_start=row["ayah_start"],
                ayah_end=row["ayah_end"],
                is_published=True,
            )
        ]
    text = normalize_arabic(row["arabic_text"])
    # Bind a short recording ONLY to an exact whole-text match, never a longer dua.
    return [
        *(
            ("arabic_item", item)
            for item in ArabicLearningItem.objects.filter(lesson__is_published=True)
            if normalize_arabic(item.arabic_text) == text
        ),
        *(
            ("dua", item)
            for item in Dua.objects.filter(is_published=True)
            if normalize_arabic(item.arabic_text) == text
        ),
    ]


@transaction.atomic
def seed_commons_audio(catalog=None):
    result = {"assets": 0, "bindings": 0, "identity_review_pending": [], "unmatched": []}
    for row in COMMONS_AUDIO_CATALOG if catalog is None else catalog:
        if row.get("identity_review_required"):
            result["identity_review_pending"].append(row["key"])
            continue
        targets = _targets(row)
        if not targets:
            result["unmatched"].append(row["key"])
            continue
        source, _ = ReligiousSource.objects.get_or_create(
            title=row["source_title"],
            defaults={
                "url": row["source_url"],
                "is_verified": True,
                "notes": f"{row['license_notes']} License: {row['license_url']}",
            },
        )
        asset, created = AudioAsset.objects.get_or_create(
            key=row["key"],
            defaults={
                "url": row["url"],
                "voice": row["voice"],
                "source": source,
                "attribution": row["attribution"],
                "license_notes": f"{row['license_notes']} {row['license_url']}",
                "rights_confirmed": True,
                # Primary creator/file identity was checked. This flag is not
                # a qualified teacher's tajweed certification; ambiguous files
                # above are intentionally not published.
                "pronunciation_verified": True,
                "is_published": True,
                "available": True,
                "provider": "wikimedia_commons",
                "checked_at": timezone.now(),
            },
        )
        asset.full_clean()
        result["assets"] += int(created)
        for field, target in targets:
            label = {language: "Audio" for language in ("uz", "ru", "en")}
            if field == "name":
                label = {"uz": "Talaffuz", "ru": "Произношение", "en": "Pronunciation"}
            elif field == "passage":
                label = {"uz": "To‘liq sura", "ru": "Полная сура", "en": "Complete surah"}
            _, new = AudioBinding.objects.get_or_create(
                asset=asset,
                **{field: target},
                defaults={"label": label},
            )
            result["bindings"] += int(new)
    return result
