from aiogram.types import BotCommand

BOT_PROFILES = {
    "ru": {
        "name": "Deenly — Исламский помощник",
        "short_description": "🌙 Имена Аллаха, аяты, дуа, када и исламский календарь в одном месте.",
        "description": "🌙 Deenly — личный исламский помощник\n\n📖 Изучайте прекрасные имена Аллаха\n🧠 Закрепляйте знания повторениями\n🤲 Читайте великие аяты и дуа\n🕌 Ведите учет када намазов и постов\n📅 Получайте напоминания о важных датах\n⭐ Собирайте личную библиотеку\n\n🌿 Маленькие постоянные шаги на пути к благому.",
        "commands": [
            ("start", "🌙 Открыть главное меню"),
            ("learn", "📖 Изучить новое имя Аллаха"),
            ("review", "🧠 Повторить изученные имена"),
            ("library", "🤲 Открыть аяты и дуа"),
            ("favorites", "⭐ Открыть избранное"),
            ("qada", "🕌 Посмотреть остаток када"),
            ("calendar", "📅 Посмотреть важные даты"),
            ("progress", "📊 Посмотреть прогресс"),
            ("settings", "⚙️ Изменить настройки"),
            ("help", "💡 Показать помощь"),
        ],
    },
    "en": {
        "name": "Deenly — Islamic Companion",
        "short_description": "🌙 Names of Allah, Quran, duas, qada, and an Islamic calendar in one place.",
        "description": "🌙 Deenly — your personal Islamic companion\n\n📖 Learn the beautiful Names of Allah\n🧠 Strengthen knowledge through reviews\n🤲 Read great Quran passages and duas\n🕌 Track qada prayers and fasts\n📅 Receive important-date reminders\n⭐ Build a personal collection\n\n🌿 Small, consistent steps toward goodness.",
        "commands": [
            ("start", "🌙 Open the main menu"),
            ("learn", "📖 Learn a new Name of Allah"),
            ("review", "🧠 Review introduced Names"),
            ("library", "🤲 Open Quran passages and duas"),
            ("favorites", "⭐ Open favorites"),
            ("qada", "🕌 View remaining qada"),
            ("calendar", "📅 View important dates"),
            ("progress", "📊 View learning progress"),
            ("settings", "⚙️ Change settings"),
            ("help", "💡 Show help"),
        ],
    },
    "uz": {
        "name": "Deenly — Islomiy hamroh",
        "short_description": "🌙 Allohning ismlari, oyatlar, duolar, qazo va islomiy taqvim bir joyda.",
        "description": "🌙 Deenly — shaxsiy islomiy hamrohingiz\n\n📖 Allohning go‘zal ismlarini o‘rganing\n🧠 Takrorlash orqali bilimni mustahkamlang\n🤲 Buyuk oyat va duolarni o‘qing\n🕌 Qazo namoz va ro‘zalarni hisoblang\n📅 Muhim sanalar haqida eslatma oling\n⭐ Shaxsiy to‘plam yarating\n\n🌿 Yaxshilik sari kichik va doimiy qadamlar.",
        "commands": [
            ("start", "🌙 Asosiy menyuni ochish"),
            ("learn", "📖 Allohning yangi ismini o‘rganish"),
            ("review", "🧠 O‘rganilgan ismlarni takrorlash"),
            ("library", "🤲 Oyat va duolarni ochish"),
            ("favorites", "⭐ Saralanganlarni ochish"),
            ("qada", "🕌 Qolgan qazoni ko‘rish"),
            ("calendar", "📅 Muhim sanalarni ko‘rish"),
            ("progress", "📊 Natijalarni ko‘rish"),
            ("settings", "⚙️ Sozlamalarni o‘zgartirish"),
            ("help", "💡 Yordamni ko‘rsatish"),
        ],
    },
}


def commands_for(language):
    return [
        BotCommand(command=command, description=description)
        for command, description in BOT_PROFILES[language]["commands"]
    ]
