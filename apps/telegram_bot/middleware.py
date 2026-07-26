from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async

from apps.users.services import PersonalBotAccessDenied, register_or_update_telegram_user

from .i18n import t


class TelegramUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        telegram_user = getattr(event, "from_user", None)
        if not telegram_user:
            return await handler(event, data)
        try:
            db_user = await sync_to_async(register_or_update_telegram_user, thread_sensitive=True)(
                telegram_user
            )
        except PersonalBotAccessDenied:
            language = (telegram_user.language_code or "ru")[:2]
            if isinstance(event, Message):
                await event.answer(t(language, "access_denied"))
            elif isinstance(event, CallbackQuery):
                await event.answer(t(language, "access_denied"), show_alert=True)
            return None
        data["db_user"] = db_user
        return await handler(event, data)
