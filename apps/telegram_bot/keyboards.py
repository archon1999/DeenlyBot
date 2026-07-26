from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .i18n import t


def main_menu(language):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(language, "learn")), KeyboardButton(text=t(language, "review"))],
            [KeyboardButton(text=t(language, "library")), KeyboardButton(text=t(language, "qada"))],
            [
                KeyboardButton(text=t(language, "calendar")),
                KeyboardButton(text=t(language, "progress")),
            ],
            [
                KeyboardButton(text=t(language, "favorites")),
                KeyboardButton(text=t(language, "settings")),
            ],
        ],
        resize_keyboard=True,
    )


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="O‘zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="English", callback_data="lang:en"),
            ]
        ]
    )


def quiz_keyboard(question):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option["label"], callback_data=f"qa:{question.id}:{index}")]
            for index, option in enumerate(question.options)
        ]
    )


def quiz_result_keyboard(language, question):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "again"), callback_data=f"again:{question.id}"
                ),
                InlineKeyboardButton(text=t(language, "continue"), callback_data="review:next"),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "details"), callback_data=f"name:{question.target_name_id}"
                )
            ],
        ]
    )


def reveal_keyboard(language, name_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(language, "show_answer"), callback_data=f"name:{name_id}")]
        ]
    )


def library_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language, "quran"), callback_data="library:quran"),
                InlineKeyboardButton(text=t(language, "duas"), callback_data="library:duas"),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "favorites"), callback_data="library:favorites"
                )
            ],
        ]
    )


def back_to_library_button(language):
    return InlineKeyboardButton(text=t(language, "back"), callback_data="library:home")
