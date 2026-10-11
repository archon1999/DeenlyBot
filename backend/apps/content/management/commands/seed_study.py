from django.core.management.base import BaseCommand

from apps.content.study_seed import seed_study_content


class Command(BaseCommand):
    help = "Add source-grounded Quran study sidecars without changing existing content or progress"

    def handle(self, *args, **options):
        result = seed_study_content()
        self.stdout.write(
            self.style.SUCCESS(
                f"Added {result['new_passages']} passages; {result['verses']} canonical verses available."
            )
        )
