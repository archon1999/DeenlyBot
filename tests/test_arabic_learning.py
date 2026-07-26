from unittest.mock import patch

import pytest
from django.core.management import call_command

from apps.arabic_learning.models import (
    ArabicItemTranslation,
    ArabicLearningItem,
    ArabicLesson,
    ArabicLessonCategory,
    ArabicLessonTranslation,
    ArabicProgressStatus,
    ArabicQuizAttempt,
    ArabicQuizType,
    UserArabicItemProgress,
    UserArabicLessonProgress,
)
from apps.arabic_learning.services import (
    answer_arabic_quiz,
    arabic_progress_stats,
    build_arabic_quiz,
    complete_lesson,
    next_lesson_for_user,
    start_lesson,
)


@pytest.fixture
def arabic_curriculum(db):
    call_command("seed_arabic", verbosity=0)
    return ArabicLesson.objects.all()


@pytest.mark.django_db
def test_arabic_seed_has_complete_multilingual_curriculum(arabic_curriculum):
    assert ArabicLesson.objects.filter(is_published=True).count() == 38
    assert ArabicLesson.objects.filter(category=ArabicLessonCategory.ALPHABET).count() == 16
    assert ArabicLesson.objects.filter(category=ArabicLessonCategory.QURAN_VOCABULARY).count() == 12
    assert ArabicLesson.objects.filter(category=ArabicLessonCategory.GRAMMAR).count() == 10
    assert ArabicLearningItem.objects.count() == 95
    assert ArabicLessonTranslation.objects.count() == 38 * 3
    assert ArabicItemTranslation.objects.count() == 95 * 3
    assert not ArabicItemTranslation.objects.filter(transcription="").exists()


@pytest.mark.django_db
def test_lesson_opens_without_completion_and_advances_only_after_confirmation(
    user, arabic_curriculum
):
    first = next_lesson_for_user(user, ArabicLessonCategory.ALPHABET)
    same_first = next_lesson_for_user(user, ArabicLessonCategory.ALPHABET)
    assert first == same_first
    assert UserArabicLessonProgress.objects.count() == 0

    lesson, progress = start_lesson(user, first.id)
    assert lesson == first
    assert progress.status == ArabicProgressStatus.IN_PROGRESS
    assert next_lesson_for_user(user, ArabicLessonCategory.ALPHABET) == first

    _, progress, created = complete_lesson(user, first.id)
    assert created is True
    assert progress.status == ArabicProgressStatus.COMPLETED
    assert UserArabicItemProgress.objects.filter(user=user).count() == first.items.count()
    assert next_lesson_for_user(user, ArabicLessonCategory.ALPHABET).order == 2


@pytest.mark.django_db
@pytest.mark.parametrize("quiz_type", list(ArabicQuizType.values[:4]))
def test_standard_arabic_quizzes_use_only_introduced_items(
    user, arabic_curriculum, quiz_type
):
    for lesson in ArabicLesson.objects.filter(category=ArabicLessonCategory.ALPHABET)[:2]:
        complete_lesson(user, lesson.id)
    target = UserArabicItemProgress.objects.filter(user=user).first().item
    with patch(
        "apps.arabic_learning.services.random.choice",
        side_effect=lambda values: quiz_type if quiz_type in values else values[0],
    ):
        question = build_arabic_quiz(user, target)

    introduced_ids = set(
        UserArabicItemProgress.objects.filter(user=user).values_list("item_id", flat=True)
    )
    assert question.quiz_type == quiz_type
    assert len(question.options) == 4
    assert {option["item_id"] for option in question.options} <= introduced_ids


@pytest.mark.django_db
def test_missing_word_quiz_and_answer_are_idempotent(user, arabic_curriculum):
    for lesson in ArabicLesson.objects.filter(
        category=ArabicLessonCategory.QURAN_VOCABULARY, order__lte=10
    ):
        complete_lesson(user, lesson.id)
    target = ArabicLearningItem.objects.get(lesson__slug="famous-quran-phrases", order=1)
    with patch(
        "apps.arabic_learning.services.random.choice",
        side_effect=lambda values: (
            ArabicQuizType.MISSING_WORD
            if ArabicQuizType.MISSING_WORD in values
            else values[0]
        ),
    ):
        question = build_arabic_quiz(user, target)

    assert question.quiz_type == ArabicQuizType.MISSING_WORD
    assert "____" in question.prompt
    answered, fresh = answer_arabic_quiz(question.id, user, question.correct_option)
    assert fresh is True
    assert answered.is_correct is True
    _, fresh_again = answer_arabic_quiz(question.id, user, question.correct_option)
    assert fresh_again is False
    assert ArabicQuizAttempt.objects.filter(question=question).count() == 1


@pytest.mark.django_db
def test_arabic_progress_stats(user, arabic_curriculum):
    lesson = ArabicLesson.objects.get(category=ArabicLessonCategory.GRAMMAR, order=1)
    complete_lesson(user, lesson.id)
    stats = arabic_progress_stats(user)
    assert stats["completed_lessons"] == 1
    assert stats["total_lessons"] == 38
    assert stats["introduced_items"] == lesson.items.count()
