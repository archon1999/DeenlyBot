import uuid

from django.db import models

from apps.content.models import NameOfAllah
from apps.core.models import Language, TimeStampedModel
from apps.users.models import TelegramUser


class LearningStatus(models.TextChoices):
    LEARNING = "learning", "Learning"
    LEARNED = "learned", "Learned"


class QuizType(models.TextChoices):
    NAME_TO_MEANING = "name_meaning", "Name → meaning"
    MEANING_TO_NAME = "meaning_name", "Meaning → name"
    NUMBER_TO_NAME = "number_name", "Number → name"
    NAME_TO_NUMBER = "name_number", "Name → number"


class UserNameProgress(TimeStampedModel):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="name_progress")
    name = models.ForeignKey(NameOfAllah, on_delete=models.CASCADE, related_name="user_progress")
    status = models.CharField(
        max_length=16, choices=LearningStatus.choices, default=LearningStatus.LEARNING
    )
    introduced_at = models.DateTimeField()
    next_review_at = models.DateTimeField()
    review_stage = models.PositiveSmallIntegerField(default=0)
    correct_streak = models.PositiveSmallIntegerField(default=0)
    total_answers = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_user_name_progress")
        ]
        ordering = ["name__order"]

    @property
    def accuracy(self):
        return self.correct_answers / self.total_answers if self.total_answers else 0


class QuizQuestion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="quiz_questions")
    target_name = models.ForeignKey(
        NameOfAllah, on_delete=models.CASCADE, related_name="quiz_questions"
    )
    quiz_type = models.CharField(max_length=20, choices=QuizType.choices)
    language = models.CharField(max_length=2, choices=Language.choices)
    prompt = models.TextField()
    options = models.JSONField(help_text="Snapshot of rendered option labels and related name IDs")
    correct_option = models.PositiveSmallIntegerField()
    answered_at = models.DateTimeField(null=True, blank=True)
    selected_option = models.PositiveSmallIntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    is_extra_practice = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class QuizAttempt(TimeStampedModel):
    question = models.OneToOneField(QuizQuestion, on_delete=models.CASCADE, related_name="attempt")
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="quiz_attempts")
    selected_option = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()

    class Meta:
        ordering = ["-created_at"]
