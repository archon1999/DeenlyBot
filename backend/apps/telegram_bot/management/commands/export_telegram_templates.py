from pathlib import Path
from string import Formatter

from django.core.management.base import BaseCommand

from apps.telegram_bot.i18n import TEXTS
from apps.telegram_bot.message_templates import TEMPLATE_MESSAGE_KEYS


def django_template_from_format(value):
    result = []
    for literal, field_name, format_spec, conversion in Formatter().parse(value):
        result.append(literal)
        if field_name is None:
            continue
        if format_spec or conversion:
            raise ValueError(f"Unsupported format expression: {field_name}")
        result.append("{{ " + field_name + " }}")
    return "".join(result)


class Command(BaseCommand):
    help = "Create missing file-based Telegram message templates from the legacy i18n catalog"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Overwrite existing templates")

    def handle(self, *args, **options):
        root = Path(__file__).resolve().parents[2] / "templates" / "telegram"
        written = 0
        for language, messages in TEXTS.items():
            language_root = root / language
            language_root.mkdir(parents=True, exist_ok=True)
            for key in sorted(TEMPLATE_MESSAGE_KEYS):
                target = language_root / f"{key}.html"
                if target.exists() and not options["force"]:
                    continue
                value = messages.get(key) or TEXTS["ru"][key]
                target.write_text(django_template_from_format(value) + "\n", encoding="utf-8")
                written += 1
        self.stdout.write(self.style.SUCCESS(f"Created {written} Telegram message templates"))
