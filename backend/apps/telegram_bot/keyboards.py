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
            [
                KeyboardButton(text=t(language, "names")),
                KeyboardButton(text=t(language, "arabic")),
            ],
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


def names_section_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(language, "names_continue"), callback_data="names:learn")],
            [
                InlineKeyboardButton(
                    text=t(language, "names_review"), callback_data="names:review"
                ),
                InlineKeyboardButton(
                    text=t(language, "names_studied"), callback_data="names:list:1"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "names_progress"), callback_data="names:progress"
                )
            ],
        ]
    )


def name_candidate_keyboard(language, name_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "name_mark_studied"),
                    callback_data=f"names:complete:{name_id}",
                )
            ],
            [InlineKeyboardButton(text=t(language, "back_to_names"), callback_data="names:home")],
        ]
    )


def arabic_dashboard_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_alphabet"),
                    callback_data="arabic:category:alphabet:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_vocabulary"),
                    callback_data="arabic:category:quran_vocabulary:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_grammar"),
                    callback_data="arabic:category:grammar:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_prayer"),
                    callback_data="arabic:category:prayer_arabic:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_sarf"), callback_data="arabic:category:sarf:1"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_daily"),
                    callback_data="arabic:category:daily_phrases:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_listening"),
                    callback_data="arabic:category:listening:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_review"), callback_data="arabic:review"
                ),
                InlineKeyboardButton(
                    text=t(language, "arabic_progress"), callback_data="arabic:progress"
                ),
            ],
        ]
    )


def arabic_lesson_keyboard(language, lesson_id, category, page):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_complete_lesson"),
                    callback_data=f"arabic:complete:{lesson_id}:{category}:{page}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_back_category"),
                    callback_data=f"arabic:category:{category}:{page}",
                )
            ],
        ]
    )


def arabic_quiz_keyboard(question):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option["label"], callback_data=f"aq:{question.id}:{index}")]
            for index, option in enumerate(question.options)
        ]
    )


def arabic_quiz_result_keyboard(language, question):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "arabic_again"), callback_data=f"arabic:again:{question.id}"
                ),
                InlineKeyboardButton(
                    text=t(language, "arabic_continue_review"),
                    callback_data="arabic:review",
                ),
            ],
            [InlineKeyboardButton(text=t(language, "arabic_back"), callback_data="arabic:home")],
        ]
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


def settings_keyboard(language, preference):
    enabled_key = "notifications_on" if preference.enabled else "notifications_off"
    weekly_key = "weekly_on" if preference.weekly_report_enabled else "weekly_off"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, enabled_key),
                    callback_data="settings:notify:toggle",
                )
            ],
            [
                InlineKeyboardButton(text="➖", callback_data="settings:notify:count_down"),
                InlineKeyboardButton(
                    text=t(
                        language,
                        "notification_count_button",
                        count=preference.random_messages_per_day,
                    ),
                    callback_data="settings:noop",
                ),
                InlineKeyboardButton(text="➕", callback_data="settings:notify:count_up"),
            ],
            [
                InlineKeyboardButton(text="◀️", callback_data="settings:notify:start_down"),
                InlineKeyboardButton(
                    text=t(
                        language,
                        "notification_start_button",
                        time=preference.random_window_start.strftime("%H:%M"),
                    ),
                    callback_data="settings:noop",
                ),
                InlineKeyboardButton(text="▶️", callback_data="settings:notify:start_up"),
            ],
            [
                InlineKeyboardButton(text="◀️", callback_data="settings:notify:end_down"),
                InlineKeyboardButton(
                    text=t(
                        language,
                        "notification_end_button",
                        time=preference.random_window_end.strftime("%H:%M"),
                    ),
                    callback_data="settings:noop",
                ),
                InlineKeyboardButton(text="▶️", callback_data="settings:notify:end_up"),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, weekly_key),
                    callback_data="settings:notify:weekly_toggle",
                )
            ],
            [InlineKeyboardButton(text=t(language, "language"), callback_data="settings:language")],
        ]
    )


def quiz_keyboard(question):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option["label"], callback_data=f"qa:{question.id}:{index}")]
            for index, option in enumerate(question.options)
        ]
        + [
            [
                InlineKeyboardButton(
                    text=t(question.language, "back_to_names"), callback_data="names:home"
                )
            ]
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
            [InlineKeyboardButton(text=t(language, "back_to_names"), callback_data="names:home")],
        ]
    )


def reveal_keyboard(language, name_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "show_answer"), callback_data=f"name:{name_id}"
                )
            ],
            [InlineKeyboardButton(text=t(language, "back_to_names"), callback_data="names:home")],
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


def quran_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "ayahs"), callback_data="library:quran:ayah:1"
                ),
                InlineKeyboardButton(
                    text=t(language, "surahs"), callback_data="library:quran:surah:1"
                ),
            ],
            [back_to_library_button(language)],
        ]
    )


def back_to_library_button(language):
    return InlineKeyboardButton(text=t(language, "back"), callback_data="library:home")
