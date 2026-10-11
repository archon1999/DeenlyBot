from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import Language, TimeStampedModel
from apps.users.models import TelegramUser


class ReligiousSource(TimeStampedModel):
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class NameOfAllah(TimeStampedModel):
    order = models.PositiveSmallIntegerField(unique=True)
    arabic = models.CharField(max_length=100)
    transliteration = models.CharField(max_length=100)
    source = models.ForeignKey(ReligiousSource, on_delete=models.PROTECT, related_name="names")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Names of Allah"

    def __str__(self):
        return f"{self.order}. {self.transliteration}"


class NameTranslation(TimeStampedModel):
    name = models.ForeignKey(NameOfAllah, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    meaning = models.CharField(max_length=255)
    transcription = models.CharField(max_length=150, blank=True)
    description = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "language"], name="unique_name_language")
        ]

    def __str__(self):
        return f"{self.name} [{self.language}]"


class QuranPassageType(models.TextChoices):
    AYAH = "ayah", "Ayah or passage"
    SURAH = "surah", "Complete surah"


class QuranPassage(TimeStampedModel):
    slug = models.SlugField(unique=True)
    surah_number = models.PositiveSmallIntegerField()
    ayah_start = models.PositiveSmallIntegerField()
    ayah_end = models.PositiveSmallIntegerField()
    passage_type = models.CharField(
        max_length=10, choices=QuranPassageType.choices, default=QuranPassageType.AYAH
    )
    arabic_text = models.TextField()
    source = models.ForeignKey(
        ReligiousSource, on_delete=models.PROTECT, related_name="quran_passages"
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["surah_number", "ayah_start"]

    def __str__(self):
        return f"{self.surah_number}:{self.ayah_start}-{self.ayah_end}"


class QuranPassageTranslation(TimeStampedModel):
    passage = models.ForeignKey(QuranPassage, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    title = models.CharField(max_length=255)
    transcription = models.TextField(blank=True)
    translation = models.TextField()
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["passage", "language"], name="unique_passage_language")
        ]


class Dua(TimeStampedModel):
    slug = models.SlugField(unique=True)
    arabic_text = models.TextField(blank=True)
    transliteration = models.TextField(blank=True)
    source = models.ForeignKey(ReligiousSource, on_delete=models.PROTECT, related_name="duas")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.slug


class DuaTranslation(TimeStampedModel):
    dua = models.ForeignKey(Dua, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    title = models.CharField(max_length=255)
    transcription = models.TextField(blank=True)
    translation = models.TextField()
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["dua", "language"], name="unique_dua_language")
        ]


class Favorite(TimeStampedModel):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="favorites")
    passage = models.ForeignKey(
        QuranPassage, null=True, blank=True, on_delete=models.CASCADE, related_name="favorites"
    )
    dua = models.ForeignKey(
        Dua, null=True, blank=True, on_delete=models.CASCADE, related_name="favorites"
    )
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(passage__isnull=False, dua__isnull=True)
                    | models.Q(passage__isnull=True, dua__isnull=False)
                ),
                name="favorite_exactly_one_content",
            ),
            models.UniqueConstraint(
                fields=["user", "passage"],
                condition=models.Q(passage__isnull=False),
                name="unique_user_passage_favorite",
            ),
            models.UniqueConstraint(
                fields=["user", "dua"],
                condition=models.Q(dua__isnull=False),
                name="unique_user_dua_favorite",
            ),
        ]

    def clean(self):
        if bool(self.passage_id) == bool(self.dua_id):
            raise ValidationError("Choose exactly one passage or dua")


class QuranVerse(TimeStampedModel):
    """Canonical verse identity shared by overlapping library passages and audio."""

    surah_number = models.PositiveSmallIntegerField()
    ayah_number = models.PositiveSmallIntegerField()
    arabic_text = models.TextField()
    source = models.ForeignKey(ReligiousSource, on_delete=models.PROTECT, related_name="verses")

    class Meta:
        ordering = ["surah_number", "ayah_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["surah_number", "ayah_number"], name="unique_quran_verse"
            ),
            models.CheckConstraint(
                condition=models.Q(surah_number__gte=1, surah_number__lte=114),
                name="verse_surah_range",
            ),
            models.CheckConstraint(
                condition=models.Q(ayah_number__gte=1, ayah_number__lte=286),
                name="verse_ayah_range",
            ),
        ]

    @property
    def key(self):
        return f"{self.surah_number}:{self.ayah_number}"

    def __str__(self):
        return self.key


class QuranVerseTranslation(TimeStampedModel):
    verse = models.ForeignKey(QuranVerse, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    translation = models.TextField()
    transcription = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["verse", "language"], name="unique_verse_language")
        ]


class QuranWord(TimeStampedModel):
    verse = models.ForeignKey(QuranVerse, on_delete=models.CASCADE, related_name="words")
    position = models.PositiveSmallIntegerField()
    arabic_text = models.CharField(max_length=100)
    root = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["verse", "position"], name="unique_quran_word_position"
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1), name="quran_word_positive_position"
            ),
        ]


class QuranWordTranslation(TimeStampedModel):
    word = models.ForeignKey(QuranWord, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=Language.choices)
    meaning = models.CharField(max_length=255)
    transcription = models.CharField(max_length=150)
    grammar_note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["word", "language"], name="unique_quran_word_language")
        ]


class QuranPassageAnalysis(TimeStampedModel):
    passage = models.OneToOneField(QuranPassage, on_delete=models.CASCADE, related_name="analysis")
    source = models.ForeignKey(
        ReligiousSource, on_delete=models.PROTECT, related_name="passage_analyses"
    )
    is_verified = models.BooleanField(default=False)


class QuranAnalysisTranslation(TimeStampedModel):
    analysis = models.ForeignKey(
        QuranPassageAnalysis, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.CharField(max_length=2, choices=Language.choices)
    summary = models.TextField()
    context = models.TextField()
    explanation = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["analysis", "language"], name="unique_analysis_language"
            )
        ]
