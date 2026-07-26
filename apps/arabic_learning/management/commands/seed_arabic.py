from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import ReligiousSource

from ...models import (
    ArabicItemTranslation,
    ArabicLearningItem,
    ArabicLesson,
    ArabicLessonTranslation,
)
from ...seed_data import ARABIC_LESSONS


class Command(BaseCommand):
    help = "Idempotently seed the multilingual Quran-focused Arabic curriculum"

    @transaction.atomic
    def handle(self, *args, **options):
        source, _ = ReligiousSource.objects.update_or_create(
            title="Quran-focused Arabic learning curriculum",
            defaults={
                "url": "https://corpus.quran.com/documentation/",
                "notes": (
                    "Foundational Arabic explanations checked against the Quranic Arabic Corpus; "
                    "verse text and references follow Quran.com. Pronunciation should be checked "
                    "with a qualified teacher."
                ),
                "is_verified": False,
            },
        )
        item_count = 0
        for data in ARABIC_LESSONS:
            lesson, _ = ArabicLesson.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "category": data["category"],
                    "order": data["order"],
                    "level": data["level"],
                    "estimated_minutes": data["minutes"],
                    "source": source,
                    "is_published": True,
                },
            )
            for language in ("ru", "en", "uz"):
                ArabicLessonTranslation.objects.update_or_create(
                    lesson=lesson,
                    language=language,
                    defaults={
                        "title": data["translations"]["title"][language],
                        "summary": data["translations"]["summary"][language],
                        "explanation": data["translations"]["explanation"][language],
                    },
                )
            expected_orders = []
            for order, item_data in enumerate(data["items"], 1):
                expected_orders.append(order)
                item, _ = ArabicLearningItem.objects.update_or_create(
                    lesson=lesson,
                    order=order,
                    defaults={
                        "item_type": item_data["type"],
                        "arabic_text": item_data["arabic"],
                        "root": item_data.get("root", ""),
                        "quran_reference": item_data.get("reference", ""),
                        "metadata": item_data.get("metadata", {}),
                    },
                )
                for language in ("ru", "en", "uz"):
                    ArabicItemTranslation.objects.update_or_create(
                        item=item,
                        language=language,
                        defaults={
                            "title": item_data["translations"]["title"][language],
                            "transcription": item_data["translations"]["transcription"][language],
                            "meaning": item_data["translations"]["meaning"][language],
                            "explanation": item_data["translations"]["explanation"][language],
                        },
                    )
                item_count += 1
            lesson.items.exclude(order__in=expected_orders).delete()

        valid_slugs = [data["slug"] for data in ARABIC_LESSONS]
        ArabicLesson.objects.exclude(slug__in=valid_slugs).update(is_published=False)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(ARABIC_LESSONS)} Arabic lessons with {item_count} learning items"
            )
        )
