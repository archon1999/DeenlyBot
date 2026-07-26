from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from apps.telegram_bot.bot import create_bot


class Command(BaseCommand):
    help = "Validate BOT_TOKEN by requesting the current Telegram bot profile"

    def handle(self, *args, **options):
        profile = async_to_sync(self.fetch_profile)()
        self.stdout.write(
            self.style.SUCCESS(
                f"Telegram connection is valid: @{profile.username} (id={profile.id})"
            )
        )

    async def fetch_profile(self):
        bot = create_bot()
        try:
            return await bot.get_me()
        finally:
            await bot.session.close()
