import json

from django.core.management.base import BaseCommand

from ...catalog_import import seed_commons_audio


class Command(BaseCommand):
    help = "Add licensed human recordings; leave ambiguous identities unpublished"

    def handle(self, *args, **options):
        result = seed_commons_audio()
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
