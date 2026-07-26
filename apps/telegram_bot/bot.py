from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings

from .arabic_handlers import router as arabic_router
from .handlers import router
from .middleware import TelegramUserMiddleware


def create_bot():
    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")
    return Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher():
    dispatcher = Dispatcher()
    middleware = TelegramUserMiddleware()
    arabic_router.message.middleware(middleware)
    arabic_router.callback_query.middleware(middleware)
    router.message.middleware(middleware)
    router.callback_query.middleware(middleware)
    dispatcher.include_router(arabic_router)
    dispatcher.include_router(router)
    return dispatcher
