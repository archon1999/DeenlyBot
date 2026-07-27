from apps.telegram_bot.keyboards import (
    back_to_library_button,
    main_menu,
    names_section_keyboard,
    quran_keyboard,
    settings_keyboard,
)
from apps.telegram_bot.profile import BOT_PROFILES, commands_for
from apps.users.models import NotificationPreference


def test_bot_profile_respects_telegram_limits_and_is_localized():
    assert set(BOT_PROFILES) == {"ru", "en", "uz"}
    for language, profile in BOT_PROFILES.items():
        assert 1 <= len(profile["name"]) <= 64
        assert len(profile["short_description"]) <= 120
        assert len(profile["description"]) <= 512
        commands = commands_for(language)
        assert 1 <= len(commands) <= 100
        command_names = {command.command for command in commands}
        assert command_names >= {
            "start",
            "names",
            "arabic",
            "qada_start",
            "qada_add",
            "help",
            "settings",
        }
        assert command_names.isdisjoint({"learn", "review"})


def test_library_back_button_targets_library_home():
    assert back_to_library_button("ru").callback_data == "library:home"


def test_main_menu_has_unified_names_and_arabic_sections():
    first_row = main_menu("ru").keyboard[0]
    assert [button.text for button in first_row] == ["✨ 99 имён Аллаха", "🔤 Арабский язык"]
    callbacks = {
        button.callback_data
        for row in names_section_keyboard("ru").inline_keyboard
        for button in row
    }
    assert callbacks >= {"names:learn", "names:review", "names:list:1", "names:progress"}


def test_quran_has_separate_ayah_and_surah_sections():
    callbacks = {
        button.callback_data
        for row in quran_keyboard("ru").inline_keyboard
        for button in row
    }
    assert callbacks >= {"library:quran:ayah:1", "library:quran:surah:1"}


def test_notification_settings_keyboard_exposes_all_controls():
    preference = NotificationPreference()
    callbacks = {
        button.callback_data
        for row in settings_keyboard("ru", preference).inline_keyboard
        for button in row
    }
    assert callbacks >= {
        "settings:notify:toggle",
        "settings:notify:count_down",
        "settings:notify:count_up",
        "settings:notify:start_down",
        "settings:notify:start_up",
        "settings:notify:end_down",
        "settings:notify:end_up",
        "settings:notify:weekly_toggle",
    }
