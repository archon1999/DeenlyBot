import asyncio

from django.core.management.base import BaseCommand

from apps.telegram_bot.bot import create_bot, create_dispatcher


class Command(BaseCommand):
    help = "Run the Deenly Telegram bot using long polling"

    def handle(self, *args, **options):
        asyncio.run(self.run())

    async def run(self):
        bot = create_bot()
        dispatcher = create_dispatcher()
        await bot.delete_webhook(drop_pending_updates=False)
        self.stdout.write(self.style.SUCCESS("DeenlyBot polling started"))
        try:
            await dispatcher.start_polling(
                bot, allowed_updates=dispatcher.resolve_used_update_types()
            )
        finally:
            await bot.session.close()
