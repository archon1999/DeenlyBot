from django.core.management.base import BaseCommand
from django.db.models import F

from apps.notifications.services import replan_daily_for_user
from apps.users.models import NotificationPreference, TelegramUser


class Command(BaseCommand):
    help = "Replace pending random notifications with half-hour schedules"

    def handle(self, *args, **options):
        users = list(
            TelegramUser.objects.filter(is_active=True).select_related("notification_preferences")
        )
        NotificationPreference.objects.filter(user__in=users).update(
            schedule_version=F("schedule_version") + 1
        )
        created = 0
        for user in TelegramUser.objects.filter(id__in=[item.id for item in users]).select_related(
            "notification_preferences"
        ):
            created += len(replan_daily_for_user(user))
        self.stdout.write(
            self.style.SUCCESS(
                f"Replanned random notifications for {len(users)} users; created {created}"
            )
        )
