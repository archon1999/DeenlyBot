from html import escape

from apps.arabic_learning.models import ArabicLessonCategory, ArabicQuizType
from apps.arabic_learning.services import localized_item, localized_lesson

from .i18n import t

CATEGORY_PRESENTATION = {
    ArabicLessonCategory.ALPHABET: ("🔤", "arabic_alphabet"),
    ArabicLessonCategory.QURAN_VOCABULARY: ("📖", "arabic_vocabulary"),
    ArabicLessonCategory.GRAMMAR: ("🧩", "arabic_grammar"),
}


def category_presentation(language, category):
    icon, key = CATEGORY_PRESENTATION[category]
    return icon, t(language, key).removeprefix(f"{icon} ")


def render_arabic_item(user, item):
    translation = localized_item(item, user.language)
    details = ""
    if translation.explanation:
        details += f"\n<i>{escape(translation.explanation)}</i>"
    if item.root:
        details += t(user.language, "arabic_root", root=escape(item.root))
    if item.quran_reference:
        details += t(
            user.language, "arabic_reference", reference=escape(item.quran_reference)
        )
    return t(
        user.language,
        "arabic_item",
        arabic=escape(item.arabic_text),
        transcription=escape(translation.transcription),
        meaning=escape(translation.meaning),
        details=details,
    )


def render_arabic_lesson(user, lesson):
    translation = localized_lesson(lesson, user.language)
    icon, _ = category_presentation(user.language, lesson.category)
    header = t(
        user.language,
        "arabic_lesson_title",
        icon=icon,
        order=lesson.order,
        title=escape(translation.title),
        minutes=lesson.estimated_minutes,
    )
    introduction = t(
        user.language,
        "arabic_lesson_summary",
        summary=escape(translation.summary),
        explanation=escape(translation.explanation),
    )
    items = "\n\n".join(render_arabic_item(user, item) for item in lesson.items.all())
    return f"{header}\n\n{introduction}\n\n{items}"


def render_arabic_quiz(user, question):
    key = {
        ArabicQuizType.ARABIC_TO_MEANING: "arabic_quiz_arabic_meaning",
        ArabicQuizType.MEANING_TO_ARABIC: "arabic_quiz_meaning_arabic",
        ArabicQuizType.ARABIC_TO_TRANSCRIPTION: "arabic_quiz_arabic_transcription",
        ArabicQuizType.TRANSCRIPTION_TO_ARABIC: "arabic_quiz_transcription_arabic",
        ArabicQuizType.MISSING_WORD: "arabic_quiz_missing_word",
    }[question.quiz_type]
    return t(user.language, key, prompt=escape(question.prompt))


def render_arabic_quiz_result(user, question):
    translation = localized_item(question.target_item, user.language)
    header = t(user.language, "correct" if question.is_correct else "incorrect")
    answer = escape(question.options[question.correct_option]["label"])
    detail = t(
        user.language,
        "arabic_correct_answer",
        answer=answer,
        arabic=escape(question.target_item.arabic_text),
        transcription=escape(translation.transcription),
        meaning=escape(translation.meaning),
    )
    return f"{header}\n\n{detail}"
