from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.learning.models import QuizAttempt, QuizType, UserNameProgress
from apps.learning.services import (
    answer_quiz,
    build_quiz,
    confirm_name_studied,
    introduce_next_name,
    next_name_for_user,
)
from apps.telegram_bot.handlers import _names_dashboard_data


@pytest.mark.django_db
def test_names_are_introduced_in_strict_order(user, four_names):
    first, _ = introduce_next_name(user)
    second, _ = introduce_next_name(user)
    assert (first.order, second.order) == (1, 2)


@pytest.mark.django_db
def test_opening_next_name_does_not_change_progress(user, four_names):
    first = next_name_for_user(user)
    same_first = next_name_for_user(user)

    assert first == same_first == four_names[0]
    assert UserNameProgress.objects.filter(user=user).count() == 0
    dashboard = _names_dashboard_data(user)
    assert dashboard["introduced"] == 0
    assert dashboard["next_name"] == "Name 1"
    assert UserNameProgress.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_name_is_added_only_after_explicit_sequential_confirmation(user, four_names):
    with pytest.raises(ValueError):
        confirm_name_studied(user, four_names[1].id)

    name, progress, created = confirm_name_studied(user, four_names[0].id)
    assert created is True
    assert name == four_names[0]
    assert progress.name == four_names[0]
    assert next_name_for_user(user) == four_names[1]

    _, same_progress, created_again = confirm_name_studied(user, four_names[0].id)
    assert created_again is False
    assert same_progress == progress


@pytest.mark.django_db
@pytest.mark.parametrize("quiz_type", list(QuizType.values))
def test_every_quiz_type_uses_only_introduced_names(user, introduced_names, quiz_type):
    target = introduced_names[0].name
    with patch(
        "apps.learning.services.random.choice",
        side_effect=lambda values: quiz_type if quiz_type in values else values[0],
    ):
        question = build_quiz(user, target)
    introduced_ids = {progress.name_id for progress in introduced_names}
    assert question.quiz_type == quiz_type
    assert len(question.options) == 4
    assert {option["name_id"] for option in question.options} == introduced_ids
    assert question.options[question.correct_option]["name_id"] == target.id


@pytest.mark.django_db
def test_quiz_requires_four_introduced_names(user, four_names):
    now = timezone.now()
    for name in four_names[:3]:
        UserNameProgress.objects.create(user=user, name=name, introduced_at=now, next_review_at=now)
    assert build_quiz(user) is None


@pytest.mark.django_db
def test_answer_is_idempotent_and_updates_progress(user, introduced_names):
    progress = introduced_names[0]
    question = build_quiz(user, progress.name)
    original_due = progress.next_review_at
    answered, fresh = answer_quiz(question.id, user, question.correct_option)
    assert fresh is True
    assert answered.is_correct is True
    progress.refresh_from_db()
    assert progress.total_answers == 1
    assert progress.correct_answers == 1
    assert progress.next_review_at > original_due

    _, fresh_again = answer_quiz(question.id, user, question.correct_option)
    progress.refresh_from_db()
    assert fresh_again is False
    assert progress.total_answers == 1
    assert QuizAttempt.objects.filter(question=question).count() == 1


@pytest.mark.django_db
def test_extra_practice_does_not_move_scheduled_review(user, introduced_names):
    progress = introduced_names[0]
    due = timezone.now() + timedelta(days=5)
    progress.next_review_at = due
    progress.save(update_fields=["next_review_at"])
    question = build_quiz(user, progress.name, extra_practice=True)
    answer_quiz(question.id, user, question.correct_option)
    progress.refresh_from_db()
    assert progress.next_review_at == due
