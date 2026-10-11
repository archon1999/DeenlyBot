import uuid

from django.db import models

from apps.content.models import Dua, QuranPassage
from apps.core.models import Language, TimeStampedModel
from apps.users.models import TelegramUser


class LibraryQuizType(models.TextChoices):
    ARABIC_TO_MEANING = "arabic_meaning", "Arabic → translation"
    MEANING_TO_ARABIC = "meaning_arabic", "Translation → Arabic"
    ARABIC_TO_TITLE = "arabic_title", "Arabic → title"
    TITLE_TO_ARABIC = "title_arabic", "Title → Arabic"
    AUDIO_TO_ARABIC = "audio_arabic", "Audio → Arabic"
    AUDIO_TO_MEANING = "audio_meaning", "Audio → translation"


class UserLibraryProgress(TimeStampedModel):
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="library_progress"
    )
    passage = models.ForeignKey(
        QuranPassage, null=True, blank=True, on_delete=models.CASCADE, related_name="user_progress"
    )
    dua = models.ForeignKey(
        Dua, null=True, blank=True, on_delete=models.CASCADE, related_name="user_progress"
    )
    introduced_at = models.DateTimeField()
    next_review_at = models.DateTimeField()
    review_stage = models.PositiveSmallIntegerField(default=0)
    correct_streak = models.PositiveSmallIntegerField(default=0)
    total_answers = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["next_review_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(passage__isnull=False, dua__isnull=True)
                    | models.Q(passage__isnull=True, dua__isnull=False)
                ),
                name="library_progress_one_content",
            ),
            models.UniqueConstraint(
                fields=["user", "passage"],
                condition=models.Q(passage__isnull=False),
                name="unique_user_library_passage",
            ),
            models.UniqueConstraint(
                fields=["user", "dua"],
                condition=models.Q(dua__isnull=False),
                name="unique_user_library_dua",
            ),
        ]

    @property
    def content(self):
        return self.dua if self.dua_id else self.passage


class LibraryQuizQuestion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="library_questions"
    )
    target_progress = models.ForeignKey(
        UserLibraryProgress, on_delete=models.CASCADE, related_name="questions"
    )
    quiz_type = models.CharField(max_length=24, choices=LibraryQuizType.choices)
    language = models.CharField(max_length=2, choices=Language.choices)
    prompt = models.TextField()
    audio_tracks = models.JSONField(default=list, blank=True)
    options = models.JSONField()
    correct_option = models.PositiveSmallIntegerField()
    answer_translation = models.TextField()
    answered_at = models.DateTimeField(null=True, blank=True)
    selected_option = models.PositiveSmallIntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    is_extra_practice = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
