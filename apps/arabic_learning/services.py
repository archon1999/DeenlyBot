import random

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.core.spaced_repetition import first_review_at, reviewed_schedule

from .models import (
    ArabicLesson,
    ArabicProgressStatus,
    ArabicQuizAttempt,
    ArabicQuizQuestion,
    ArabicQuizType,
    UserArabicItemProgress,
    UserArabicLessonProgress,
)


def _localized(related_manager, language):
    cached = list(related_manager.all())
    return next(
        (item for item in cached if item.language == language),
        next((item for item in cached if item.language == "ru"), cached[0] if cached else None),
    )


def localized_lesson(lesson, language):
    return _localized(lesson.translations, language)


def localized_item(item, language):
    return _localized(item.translations, language)


def lesson_with_content(lesson_id):
    return (
        ArabicLesson.objects.select_related("source")
        .prefetch_related("translations", "items__translations")
        .get(id=lesson_id, is_published=True)
    )


def next_lesson_for_user(user, category):
    completed = UserArabicLessonProgress.objects.filter(
        user=user, status=ArabicProgressStatus.COMPLETED
    ).values_list("lesson_id", flat=True)
    return (
        ArabicLesson.objects.filter(category=category, is_published=True)
        .exclude(id__in=completed)
        .prefetch_related("translations")
        .order_by("order")
        .first()
    )


@transaction.atomic
def start_lesson(user, lesson_id):
    lesson = lesson_with_content(lesson_id)
    progress, _ = UserArabicLessonProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={"started_at": timezone.now()},
    )
    return lesson, progress


@transaction.atomic
def complete_lesson(user, lesson_id):
    lesson = lesson_with_content(lesson_id)
    now = timezone.now()
    progress, _ = UserArabicLessonProgress.objects.select_for_update().get_or_create(
        user=user,
        lesson=lesson,
        defaults={"started_at": now},
    )
    newly_completed = progress.status != ArabicProgressStatus.COMPLETED
    progress.status = ArabicProgressStatus.COMPLETED
    progress.completed_at = progress.completed_at or now
    progress.save(update_fields=["status", "completed_at", "updated_at"])
    for item in lesson.items.all():
        UserArabicItemProgress.objects.get_or_create(
            user=user,
            item=item,
            defaults={"introduced_at": now, "next_review_at": first_review_at(now)},
        )
    return lesson, progress, newly_completed


def select_arabic_review_target(user):
    progress = UserArabicItemProgress.objects.filter(user=user).select_related("item")
    return (
        progress.filter(next_review_at__lte=timezone.now()).order_by(
            "next_review_at", "review_stage"
        ).first()
        or progress.order_by("next_review_at").first()
    )


def _standard_quiz_parts(quiz_type, item, translation):
    if quiz_type == ArabicQuizType.ARABIC_TO_MEANING:
        return item.arabic_text, "meaning"
    if quiz_type == ArabicQuizType.MEANING_TO_ARABIC:
        return translation.meaning, "arabic"
    if quiz_type == ArabicQuizType.ARABIC_TO_TRANSCRIPTION:
        return item.arabic_text, "transcription"
    return translation.transcription, "arabic"


@transaction.atomic
def build_arabic_quiz(user, target_item=None, *, extra_practice=False, exclude_type=None):
    progress = list(
        UserArabicItemProgress.objects.filter(user=user)
        .select_related("item")
        .prefetch_related("item__translations")
    )
    if len(progress) < 4:
        return None
    target_progress = next(
        (entry for entry in progress if entry.item_id == getattr(target_item, "id", None)), None
    )
    target_progress = target_progress or select_arabic_review_target(user) or random.choice(progress)
    target = next(entry.item for entry in progress if entry.item_id == target_progress.item_id)
    translation = localized_item(target, user.language)
    standard_types = [
        ArabicQuizType.ARABIC_TO_MEANING,
        ArabicQuizType.MEANING_TO_ARABIC,
        ArabicQuizType.ARABIC_TO_TRANSCRIPTION,
        ArabicQuizType.TRANSCRIPTION_TO_ARABIC,
    ]
    available_types = [quiz_type for quiz_type in standard_types if quiz_type != exclude_type]
    if target.metadata.get("missing_word") and exclude_type != ArabicQuizType.MISSING_WORD:
        available_types.append(ArabicQuizType.MISSING_WORD)
    quiz_type = random.choice(available_types)

    if quiz_type == ArabicQuizType.MISSING_WORD:
        answer = target.metadata["missing_word"]
        prompt = target.arabic_text.replace(answer, "____", 1)
        labels = list(dict.fromkeys(target.metadata.get("missing_options", [])))
        if answer not in labels:
            labels.insert(0, answer)
        labels = labels[:4]
        random.shuffle(labels)
        options = [{"label": label, "item_id": target.id} for label in labels]
        correct_option = labels.index(answer)
    else:
        prompt, option_kind = _standard_quiz_parts(quiz_type, target, translation)
        candidates = []
        for entry in progress:
            item_translation = localized_item(entry.item, user.language)
            label = {
                "meaning": item_translation.meaning,
                "arabic": entry.item.arabic_text,
                "transcription": item_translation.transcription,
            }[option_kind]
            if label and all(existing[0] != label for existing in candidates):
                candidates.append((label, entry.item_id))
        target_label = {
            "meaning": translation.meaning,
            "arabic": target.arabic_text,
            "transcription": translation.transcription,
        }[option_kind]
        distractors = random.sample(
            [candidate for candidate in candidates if candidate[1] != target.id], 3
        )
        selected = [(target_label, target.id), *distractors]
        random.shuffle(selected)
        options = [{"label": label, "item_id": item_id} for label, item_id in selected]
        correct_option = next(
            index for index, option in enumerate(options) if option["item_id"] == target.id
        )

    return ArabicQuizQuestion.objects.create(
        user=user,
        target_item=target,
        quiz_type=quiz_type,
        language=user.language,
        prompt=prompt,
        options=options,
        correct_option=correct_option,
        is_extra_practice=extra_practice,
    )


@transaction.atomic
def answer_arabic_quiz(question_id, user, selected_option):
    question = (
        ArabicQuizQuestion.objects.select_for_update()
        .select_related("target_item")
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
    question.save(
        update_fields=["selected_option", "is_correct", "answered_at", "updated_at"]
    )
    ArabicQuizAttempt.objects.create(
        question=question,
        user=user,
        selected_option=selected_option,
        is_correct=is_correct,
    )
    progress = UserArabicItemProgress.objects.select_for_update().get(
        user=user, item=question.target_item
    )
    progress.total_answers += 1
    if is_correct:
        progress.correct_answers += 1
        progress.correct_streak += 1
    else:
        progress.correct_streak = 0
    if not question.is_extra_practice:
        progress.review_stage, progress.next_review_at = reviewed_schedule(
            progress.review_stage, is_correct
        )
    progress.save()
    return question, True


def arabic_progress_stats(user):
    lessons = UserArabicLessonProgress.objects.filter(user=user)
    items = UserArabicItemProgress.objects.filter(user=user)
    aggregate = items.aggregate(answers=Sum("total_answers"), correct=Sum("correct_answers"))
    answers = aggregate["answers"] or 0
    correct = aggregate["correct"] or 0
    return {
        "completed_lessons": lessons.filter(status=ArabicProgressStatus.COMPLETED).count(),
        "total_lessons": ArabicLesson.objects.filter(is_published=True).count(),
        "introduced_items": items.count(),
        "due_items": items.filter(next_review_at__lte=timezone.now()).count(),
        "answers": answers,
        "accuracy": round(correct * 100 / answers) if answers else 0,
    }
