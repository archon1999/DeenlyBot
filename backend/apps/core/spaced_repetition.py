from datetime import timedelta

from django.utils import timezone

REVIEW_INTERVALS = (
    timedelta(minutes=10),
    timedelta(days=1),
    timedelta(days=3),
    timedelta(days=7),
    timedelta(days=14),
    timedelta(days=30),
)


def first_review_at(now=None):
    return (now or timezone.now()) + REVIEW_INTERVALS[0]


def reviewed_schedule(stage, is_correct, now=None):
    now = now or timezone.now()
    if is_correct:
        stage = min(stage + 1, len(REVIEW_INTERVALS) - 1)
    else:
        stage = max(0, stage - 1)
    return stage, now + REVIEW_INTERVALS[stage if is_correct else 0]
