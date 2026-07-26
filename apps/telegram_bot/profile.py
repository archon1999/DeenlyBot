from aiogram.types import BotCommand

BOT_PROFILES = {
    "ru": {
        "name": "Deenly — Исламский помощник",
        "short_description": "🌙 Имена Аллаха, арабский Корана, аяты, дуа, када и календарь.",
        "description": "🌙 Deenly — личный исламский помощник\n\n✨ Изучайте 99 имён Аллаха\n🔤 Осваивайте алфавит, слова Корана и грамматику\n🧠 Закрепляйте знания повторениями\n🤲 Читайте великие аяты и дуа\n🕌 Ведите учет када намазов и постов\n📅 Получайте напоминания о важных датах\n⭐ Собирайте личную библиотеку\n\n🌿 Маленькие постоянные шаги на пути к благому.",
        "commands": [
            ("start", "🌙 Открыть главное меню"),
            ("names", "✨ Открыть 99 имён Аллаха"),
            ("arabic", "🔤 Изучать арабский язык Корана"),
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
        "short_description": "🌙 Names of Allah, Quranic Arabic, Quran, duas, qada, and calendar.",
        "description": "🌙 Deenly — your personal Islamic companion\n\n✨ Learn the 99 Names of Allah\n🔤 Study the alphabet, Quran words, and grammar\n🧠 Strengthen knowledge through reviews\n🤲 Read great Quran passages and duas\n🕌 Track qada prayers and fasts\n📅 Receive important-date reminders\n⭐ Build a personal collection\n\n🌿 Small, consistent steps toward goodness.",
        "commands": [
            ("start", "🌙 Open the main menu"),
            ("names", "✨ Open the 99 Names of Allah"),
            ("arabic", "🔤 Study the Arabic of the Quran"),
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
        "short_description": "🌙 Allohning ismlari, Qur’on arab tili, oyatlar, duolar, qazo va taqvim.",
        "description": "🌙 Deenly — shaxsiy islomiy hamrohingiz\n\n✨ Allohning 99 ismini o‘rganing\n🔤 Alifbo, Qur’on so‘zlari va grammatikani o‘rganing\n🧠 Takrorlash orqali bilimni mustahkamlang\n🤲 Buyuk oyat va duolarni o‘qing\n🕌 Qazo namoz va ro‘zalarni hisoblang\n📅 Muhim sanalar haqida eslatma oling\n⭐ Shaxsiy to‘plam yarating\n\n🌿 Yaxshilik sari kichik va doimiy qadamlar.",
        "commands": [
            ("start", "🌙 Asosiy menyuni ochish"),
            ("names", "✨ Allohning 99 ismini ochish"),
            ("arabic", "🔤 Qur’on arab tilini o‘rganish"),
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
