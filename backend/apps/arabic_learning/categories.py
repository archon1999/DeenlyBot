"""Shared category presentation for the website and Telegram bot."""

from .models import ArabicLessonCategory

CATEGORY_TRANSLATIONS = {
    "alphabet": {
        "ru": ("Алфавит и чтение", "Буквы, огласовки и соединение букв."),
        "en": ("Alphabet and reading", "Letters, vowel marks and joined forms."),
        "uz": ("Alifbo va o‘qish", "Harflar, harakatlar va harflarning ulanishi."),
    },
    "quran_vocabulary": {
        "ru": ("Слова Корана", "Частые слова и выражения с кораническими примерами."),
        "en": ("Quran words", "Common words and expressions with Quran examples."),
        "uz": ("Qur’on so‘zlari", "Qur’ondagi ko‘p uchraydigan so‘zlar va iboralar."),
    },
    "grammar": {
        "ru": ("Нахв", "Построение предложений и полезные языковые факты."),
        "en": ("Nahw", "Sentence structure and useful language facts."),
        "uz": ("Nahv", "Gap tuzilishi va foydali til faktlari."),
    },
    "prayer_arabic": {
        "ru": ("Арабский язык намаза", "Понимание слов и выражений в молитве."),
        "en": ("Prayer Arabic", "Understand the words and expressions of prayer."),
        "uz": ("Namoz arabchasi", "Namozdagi so‘zlar va iboralarni tushunish."),
    },
    "sarf": {
        "ru": ("Сарф", "Корни, формы слов, времена и число."),
        "en": ("Sarf", "Roots, word patterns, verb forms and number."),
        "uz": ("Sarf", "O‘zaklar, so‘z qoliplari, fe’l shakllari va son."),
    },
    "daily_phrases": {
        "ru": ("Повседневные выражения", "Приветствия, знакомство и простые просьбы."),
        "en": ("Everyday expressions", "Greetings, introductions and simple requests."),
        "uz": ("Kundalik iboralar", "Salomlashish, tanishish va oddiy iltimoslar."),
    },
    "listening": {
        "ru": ("Аудирование", "Учитесь узнавать текст и смысл на слух."),
        "en": ("Listening comprehension", "Recognise text and meaning by listening."),
        "uz": ("Tinglab tushunish", "Audiodan matn va ma’noni tanishni o‘rganing."),
    },
}


def categories_for_language(language):
    language = language if language in {"ru", "en", "uz"} else "en"
    return [
        {
            "key": category.value,
            "title": CATEGORY_TRANSLATIONS[category.value][language][0],
            "description": CATEGORY_TRANSLATIONS[category.value][language][1],
        }
        for category in ArabicLessonCategory
    ]
