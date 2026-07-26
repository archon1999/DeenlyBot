from aiogram.types import MenuButtonCommands
from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from apps.telegram_bot.bot import create_bot
from apps.telegram_bot.profile import BOT_PROFILES, commands_for


class Command(BaseCommand):
    help = "Update localized Telegram bot name, descriptions, commands, and menu button"

    def handle(self, *args, **options):
        updated = async_to_sync(self.update_profile)()
        for language in updated:
            self.stdout.write(self.style.SUCCESS(f"Updated Telegram profile [{language}]"))

    async def update_profile(self):
        bot = create_bot()
        try:
            for language, profile in BOT_PROFILES.items():
                await bot.set_my_name(name=profile["name"], language_code=language)
                await bot.set_my_short_description(
                    short_description=profile["short_description"], language_code=language
                )
                await bot.set_my_description(
                    description=profile["description"], language_code=language
                )
                await bot.set_my_commands(commands_for(language), language_code=language)

            default = BOT_PROFILES["ru"]
            await bot.set_my_name(name=default["name"])
            await bot.set_my_short_description(short_description=default["short_description"])
            await bot.set_my_description(description=default["description"])
            await bot.set_my_commands(commands_for("ru"))
            await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

            for language, profile in BOT_PROFILES.items():
                actual_name = await bot.get_my_name(language_code=language)
                actual_commands = await bot.get_my_commands(language_code=language)
                if actual_name.name != profile["name"] or len(actual_commands) != len(
                    profile["commands"]
                ):
                    raise RuntimeError(f"Telegram profile verification failed for {language}")
            return list(BOT_PROFILES)
        finally:
            await bot.session.close()
