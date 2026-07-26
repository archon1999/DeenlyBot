from apps.telegram_bot.i18n import TEXTS, t


def test_all_languages_have_the_same_interface_keys():
    expected = set(TEXTS["ru"])
    assert set(TEXTS["en"]) == expected
    assert set(TEXTS["uz"]) == expected


def test_unknown_language_falls_back_to_russian():
    assert t("xx", "menu") == TEXTS["ru"]["menu"]


def test_user_facing_content_templates_do_not_expose_sources():
    for translations in TEXTS.values():
        for key in ("name_card", "passage", "dua_card"):
            assert "{source}" not in translations[key]
