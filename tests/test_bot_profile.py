from apps.telegram_bot.keyboards import back_to_library_button
from apps.telegram_bot.profile import BOT_PROFILES, commands_for


def test_bot_profile_respects_telegram_limits_and_is_localized():
    assert set(BOT_PROFILES) == {"ru", "en", "uz"}
    for language, profile in BOT_PROFILES.items():
        assert 1 <= len(profile["name"]) <= 64
        assert len(profile["short_description"]) <= 120
        assert len(profile["description"]) <= 512
        commands = commands_for(language)
        assert 1 <= len(commands) <= 100
        assert {command.command for command in commands} >= {"start", "help", "settings"}


def test_library_back_button_targets_library_home():
    assert back_to_library_button("ru").callback_data == "library:home"
