from html import escape

from apps.content.services import localized_name
from apps.learning.models import QuizType

from .i18n import t


def render_name_card(user, name):
    translation = localized_name(name, user.language)
    return t(
        user.language,
        "name_card",
        order=name.order,
        transcription=escape(translation.transcription or name.transliteration),
        arabic=escape(name.arabic),
        meaning=escape(translation.meaning),
        description=escape(translation.description),
    )


def render_quiz(user, question):
    key = {
        QuizType.NAME_TO_MEANING: "quiz_name_meaning",
        QuizType.MEANING_TO_NAME: "quiz_meaning_name",
        QuizType.NUMBER_TO_NAME: "quiz_number_name",
        QuizType.NAME_TO_NUMBER: "quiz_name_number",
    }[question.quiz_type]
    return t(user.language, key, prompt=escape(question.prompt))


def render_quiz_result(user, question):
    translation = localized_name(question.target_name, user.language)
    header = t(user.language, "correct" if question.is_correct else "incorrect")
    answer = escape(question.options[question.correct_option]["label"])
    detail = t(
        user.language,
        "correct_answer",
        answer=answer,
        name=escape(translation.transcription or question.target_name.transliteration),
        meaning=escape(translation.meaning),
        description=escape(translation.description),
    )
    return f"{header}\n\n{detail}"
