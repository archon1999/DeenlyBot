import json

from django.core.management.base import BaseCommand, CommandError

from ...quran_foundation import QuranFoundationError
from ...sync import refresh_quran_audio
from ...tasks import ensure_audio_schedule


class Command(BaseCommand):
    help = "Fetch approved Quran Foundation audio metadata without downloading recordings"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=8)

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 200:
            raise CommandError("--limit must be between 1 and 200.")
        try:
            result = refresh_quran_audio(limit=options["limit"])
        except QuranFoundationError as error:
            raise CommandError(str(error)) from None
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        ensure_audio_schedule()
        if result["failed"]:
            raise CommandError("Some ayahs could not be synchronized; see the references above.")
