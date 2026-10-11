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

    def add_arguments(self, parser):
        parser.add_argument(
            "--add-only", action="store_true", help="Preserve all existing reviewed content"
        )

    def seed(self, model, **kwargs):
        method = model.objects.get_or_create if self.add_only else model.objects.update_or_create
        return method(**kwargs)

    @transaction.atomic
    def handle(self, *args, **options):
        self.add_only = options.get("add_only", False)
        source, _ = self.seed(
            ReligiousSource,
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
            lesson_source = source
            if source_data := data.get("source"):
                lesson_source, _ = self.seed(
                    ReligiousSource,
                    title=source_data["title"],
                    defaults={
                        "url": source_data["url"],
                        "notes": source_data["notes"],
                        "is_verified": False,
                    },
                )
            lesson, _ = self.seed(
                ArabicLesson,
                slug=data["slug"],
                defaults={
                    "category": data["category"],
                    "order": data["order"],
                    "level": data["level"],
                    "estimated_minutes": data["minutes"],
                    "source": lesson_source,
                    "is_published": True,
                },
            )
            for language in ("ru", "en", "uz"):
                self.seed(
                    ArabicLessonTranslation,
                    lesson=lesson,
                    language=language,
                    defaults={
                        "title": data["translations"]["title"][language],
                        "summary": data["translations"]["summary"][language],
                        "explanation": data["translations"]["explanation"][language],
                    },
                )
            for order, item_data in enumerate(data["items"], 1):
                item, _ = self.seed(
                    ArabicLearningItem,
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
                    self.seed(
                        ArabicItemTranslation,
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
            # A reduced/reorganised seed must not cascade-delete item progress,
            # attempts or administrator-added cards. Retiring content is a
            # separate explicit operation; rerunning this command is additive.
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(ARABIC_LESSONS)} Arabic lessons with {item_count} learning items"
            )
        )
