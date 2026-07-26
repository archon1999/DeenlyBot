import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.content.models import NameOfAllah
from apps.content.services import localized_name

from .models import LearningStatus, QuizAttempt, QuizQuestion, QuizType, UserNameProgress

REVIEW_INTERVALS = [
    timedelta(minutes=10),
    timedelta(days=1),
    timedelta(days=3),
    timedelta(days=7),
    timedelta(days=14),
    timedelta(days=30),
]


@transaction.atomic
def introduce_next_name(user):
    introduced_ids = UserNameProgress.objects.filter(user=user).values_list("name_id", flat=True)
    name = (
        NameOfAllah.objects.filter(is_published=True)
        .exclude(id__in=introduced_ids)
        .order_by("order")
        .first()
    )
    if not name:
        return None, None
    now = timezone.now()
    progress = UserNameProgress.objects.create(
        user=user,
        name=name,
        introduced_at=now,
        next_review_at=now + REVIEW_INTERVALS[0],
    )
    return name, progress


def select_review_target(user):
    now = timezone.now()
    return (
        UserNameProgress.objects.filter(user=user, next_review_at__lte=now)
        .select_related("name")
        .order_by("next_review_at", "review_stage")
        .first()
        or UserNameProgress.objects.filter(user=user)
        .select_related("name")
        .order_by("next_review_at")
        .first()
    )


def _question_parts(quiz_type, target, target_translation):
    if quiz_type == QuizType.NAME_TO_MEANING:
        return target_translation.transcription or target.transliteration, "meaning"
    if quiz_type == QuizType.MEANING_TO_NAME:
        return target_translation.meaning, "name"
    if quiz_type == QuizType.NUMBER_TO_NAME:
        return str(target.order), "name"
    return target_translation.transcription or target.transliteration, "number"


@transaction.atomic
def build_quiz(user, target_name=None, *, extra_practice=False, exclude_type=None):
    progress = list(
        UserNameProgress.objects.filter(user=user).select_related("name").order_by("name__order")
    )
    if len(progress) < 4:
        return None
    target_progress = next(
        (p for p in progress if p.name_id == getattr(target_name, "id", None)), None
    )
    target_progress = target_progress or select_review_target(user) or random.choice(progress)
    target = target_progress.name
    available_types = [value for value, _ in QuizType.choices if value != exclude_type] or list(
        QuizType.values
    )
    quiz_type = random.choice(available_types)
    distractors = random.sample([p.name for p in progress if p.name_id != target.id], 3)
    names = [target, *distractors]
    random.shuffle(names)
    translations = {name.id: localized_name(name, user.language) for name in names}
    target_translation = translations[target.id]
    prompt, option_kind = _question_parts(quiz_type, target, target_translation)
    options = []
    for name in names:
        label = {
            "meaning": translations[name.id].meaning,
            "name": translations[name.id].transcription or name.transliteration,
            "number": str(name.order),
        }[option_kind]
        options.append({"label": label, "name_id": name.id})
    correct_option = next(
        index for index, option in enumerate(options) if option["name_id"] == target.id
    )
    return QuizQuestion.objects.create(
        user=user,
        target_name=target,
        quiz_type=quiz_type,
        language=user.language,
        prompt=prompt,
        options=options,
        correct_option=correct_option,
        is_extra_practice=extra_practice,
    )


@transaction.atomic
def answer_quiz(question_id, user, selected_option):
    question = (
        QuizQuestion.objects.select_for_update()
        .select_related("target_name")
        .get(id=question_id, user=user)
    )
    if question.answered_at is not None:
        return question, False
    if selected_option < 0 or selected_option >= len(question.options):
        raise ValueError("Invalid option")
    is_correct = selected_option == question.correct_option
    question.selected_option = selected_option
    question.is_correct = is_correct
    question.answered_at = timezone.now()
    question.save(update_fields=["selected_option", "is_correct", "answered_at", "updated_at"])
    QuizAttempt.objects.create(
        question=question, user=user, selected_option=selected_option, is_correct=is_correct
    )

    progress = UserNameProgress.objects.select_for_update().get(
        user=user, name=question.target_name
    )
    progress.total_answers += 1
    if is_correct:
        progress.correct_answers += 1
        progress.correct_streak += 1
        if not question.is_extra_practice:
            progress.review_stage = min(progress.review_stage + 1, len(REVIEW_INTERVALS) - 1)
            progress.next_review_at = timezone.now() + REVIEW_INTERVALS[progress.review_stage]
        if progress.correct_streak >= 4 and progress.review_stage >= 3:
            progress.status = LearningStatus.LEARNED
    else:
        progress.correct_streak = 0
        if not question.is_extra_practice:
            progress.review_stage = max(0, progress.review_stage - 1)
            progress.next_review_at = timezone.now() + REVIEW_INTERVALS[0]
        progress.status = LearningStatus.LEARNING
    progress.save()
    return question, True
