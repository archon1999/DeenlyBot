from django.template import Context, TemplateDoesNotExist, engines

TEMPLATE_MESSAGE_KEYS = {
    "welcome",
    "help",
    "names_section",
    "name_card",
    "review_intro",
    "correct_answer",
    "progress_text",
    "arabic_dashboard",
    "arabic_category_title",
    "arabic_lesson_title",
    "arabic_lesson_summary",
    "arabic_item",
    "arabic_recall",
    "arabic_correct_answer",
    "arabic_progress_text",
    "library_title",
    "quran_choose",
    "ayahs_page",
    "surahs_page",
    "duas_page",
    "passage",
    "dua_card",
    "favorites_empty",
    "favorites_title",
    "qada_title",
    "qada_current",
    "calendar_title",
    "weekly_report",
    "settings_title",
    "event_reminder",
}


def render_message_template(language, key, context):
    engine = engines["django"].engine
    language = language if language in {"ru", "en", "uz"} else "ru"
    try:
        template = engine.get_template(f"telegram/{language}/{key}.html")
    except TemplateDoesNotExist:
        template = engine.get_template(f"telegram/ru/{key}.html")
    return template.render(Context(context, autoescape=False)).strip()
