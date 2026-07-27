from pathlib import Path

import pytest
from django.conf import settings

from apps.telegram_bot.i18n import t
from apps.telegram_bot.message_templates import TEMPLATE_MESSAGE_KEYS


def test_every_rich_message_has_a_template_for_each_language():
    root = Path(settings.BASE_DIR) / "apps" / "telegram_bot" / "templates" / "telegram"
    missing = [
        f"{language}/{key}.html"
        for language in ("ru", "en", "uz")
        for key in TEMPLATE_MESSAGE_KEYS
        if not (root / language / f"{key}.html").is_file()
    ]
    assert missing == []


@pytest.mark.parametrize("language", ["ru", "en", "uz"])
def test_names_dashboard_no_longer_contains_progress_disclaimer(language):
    rendered = t(
        language,
        "names_section",
        introduced=1,
        total=100,
        today=1,
        due=0,
        next_name="Ar-Rahman",
    )
    assert "Открытие раздела" not in rendered
    assert "Opening this section" not in rendered
    assert "Bo‘limni ochish" not in rendered


def test_django_message_template_renders_context():
    rendered = t(
        "ru",
        "qada_current",
        date="27.07.2026",
        prayer="Фаджр",
        source="пропущен после начальной даты",
    )
    assert "27.07.2026" in rendered
    assert "Фаджр" in rendered
    assert "{{" not in rendered
