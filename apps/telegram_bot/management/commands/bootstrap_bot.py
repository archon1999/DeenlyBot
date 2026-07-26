from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.notifications.schedules import ensure_schedules


class Command(BaseCommand):
    help = "Seed religious content and create Django Q schedules"

    def handle(self, *args, **options):
        call_command("seed_content")
        call_command("seed_arabic")
        ensure_schedules()
        self.stdout.write(self.style.SUCCESS("Content and schedules are ready"))
