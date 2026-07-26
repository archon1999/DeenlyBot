import uuid

from django.db import models

from apps.content.models import ReligiousSource
from apps.core.models import Language, TimeStampedModel
from apps.users.models import TelegramUser


class ArabicLessonCategory(models.TextChoices):
    ALPHABET = "alphabet", "Alphabet"
    QURAN_VOCABULARY = "quran_vocabulary", "Quran words and phrases"
    GRAMMAR = "grammar", "Grammar and facts"


class ArabicItemType(models.TextChoices):
    LETTER = "letter", "Letter"
    WORD = "word", "Word"
    PHRASE = "phrase", "Phrase"
    EXAMPLE = "example", "Grammar example"
    FACT = "fact", "Language fact"


class ArabicProgressStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"


class ArabicQuizType(models.TextChoices):
    ARABIC_TO_MEANING = "arabic_meaning", "Arabic → meaning"
    MEANING_TO_ARABIC = "meaning_arabic", "Meaning → Arabic"
    ARABIC_TO_TRANSCRIPTION = "arabic_transcription", "Arabic → transcription"
    TRANSCRIPTION_TO_ARABIC = "transcription_arabic", "Transcription → Arabic"
    MISSING_WORD = "missing_word", "Missing word"


class ArabicLesson(TimeStampedModel):
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=24, choices=ArabicLessonCategory.choices)
    order = models.PositiveSmallIntegerField()
    level = models.PositiveSmallIntegerField(default=1)
    estimated_minutes = models.PositiveSmallIntegerField(default=5)
    source = models.ForeignKey(
        ReligiousSource, on_delete=models.PROTECT, related_name="arabic_lessons"
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "order"], name="unique_arabic_lesson_category_order"
            )
        ]

    def __str__(self):
        return f"{self.get_category_display()} #{self.order}: {self.slug}"


class ArabicLessonTranslation(TimeStampedModel):
    lesson = models.ForeignKey(ArabicLesson, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    explanation = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "language"], name="unique_arabic_lesson_language"
            )
        ]

    def __str__(self):
        return f"{self.lesson.slug} [{self.language}]"


class ArabicLearningItem(TimeStampedModel):
    lesson = models.ForeignKey(ArabicLesson, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveSmallIntegerField()
    item_type = models.CharField(max_length=16, choices=ArabicItemType.choices)
    arabic_text = models.TextField()
    root = models.CharField(max_length=32, blank=True)
    quran_reference = models.CharField(max_length=50, blank=True)
    audio_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["lesson__category", "lesson__order", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "order"], name="unique_arabic_item_lesson_order"
            )
        ]

    def __str__(self):
        return f"{self.lesson.slug} #{self.order}: {self.arabic_text[:40]}"


class ArabicItemTranslation(TimeStampedModel):
    item = models.ForeignKey(
        ArabicLearningItem, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.CharField(max_length=2, choices=Language.choices)
    title = models.CharField(max_length=255)
    transcription = models.TextField(blank=True)
    meaning = models.TextField()
    explanation = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "language"], name="unique_arabic_item_language"
            )
        ]

    def __str__(self):
        return f"{self.item} [{self.language}]"


class UserArabicLessonProgress(TimeStampedModel):
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="arabic_lesson_progress"
    )
    lesson = models.ForeignKey(
        ArabicLesson, on_delete=models.CASCADE, related_name="user_progress"
    )
    status = models.CharField(
        max_length=16,
        choices=ArabicProgressStatus.choices,
        default=ArabicProgressStatus.IN_PROGRESS,
    )
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    best_score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"], name="unique_user_arabic_lesson_progress"
            )
        ]
        ordering = ["lesson__category", "lesson__order"]


class UserArabicItemProgress(TimeStampedModel):
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="arabic_item_progress"
    )
    item = models.ForeignKey(
        ArabicLearningItem, on_delete=models.CASCADE, related_name="user_progress"
    )
    introduced_at = models.DateTimeField()
    next_review_at = models.DateTimeField()
    review_stage = models.PositiveSmallIntegerField(default=0)
    correct_streak = models.PositiveSmallIntegerField(default=0)
    total_answers = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "item"], name="unique_user_arabic_item_progress"
            )
        ]
        ordering = ["next_review_at"]

    @property
    def accuracy(self):
        return self.correct_answers / self.total_answers if self.total_answers else 0


class ArabicQuizQuestion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="arabic_quiz_questions"
    )
    target_item = models.ForeignKey(
        ArabicLearningItem, on_delete=models.CASCADE, related_name="quiz_questions"
    )
    quiz_type = models.CharField(max_length=28, choices=ArabicQuizType.choices)
    language = models.CharField(max_length=2, choices=Language.choices)
    prompt = models.TextField()
    options = models.JSONField()
    correct_option = models.PositiveSmallIntegerField()
    answered_at = models.DateTimeField(null=True, blank=True)
    selected_option = models.PositiveSmallIntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    is_extra_practice = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class ArabicQuizAttempt(TimeStampedModel):
    question = models.OneToOneField(
        ArabicQuizQuestion, on_delete=models.CASCADE, related_name="attempt"
    )
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="arabic_quiz_attempts"
    )
    selected_option = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()

    class Meta:
        ordering = ["-created_at"]
