import ipaddress
import uuid
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


def validate_audio_url(value):
    if not value:
        return
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme != "https"
        or not host
        or parsed.username
        or parsed.password
        or host in {"localhost", "localhost.localdomain"}
        or host.endswith((".local", ".internal", ".localhost"))
    ):
        raise ValidationError("Audio must use a public HTTPS URL without credentials.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return
    if not address.is_global:
        raise ValidationError("Private network audio URLs are not allowed.")


class AudioAsset(TimeStampedModel):
    """A real recording and its rights/availability, independent of an exercise."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=1000, blank=True, validators=[validate_audio_url])
    file = models.FileField(
        upload_to="study_audio/",
        blank=True,
        validators=[FileExtensionValidator(["mp3", "ogg", "wav", "m4a"])],
    )
    voice = models.CharField(max_length=150)
    source = models.ForeignKey(
        "content.ReligiousSource", on_delete=models.PROTECT, related_name="audio_assets"
    )
    attribution = models.CharField(max_length=500)
    license_notes = models.TextField()
    rights_confirmed = models.BooleanField(default=False)
    pronunciation_verified = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    segments = models.JSONField(default=list, blank=True)
    provider = models.CharField(max_length=40, default="manual")
    checked_at = models.DateTimeField(null=True, blank=True)
    # API audio URL metadata is not permission to indefinitely store recordings.
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(url="") & ~models.Q(file=""))
                | (~models.Q(url="") & models.Q(file="")),
                name="audio_exactly_one_location",
            ),
        ]

    def clean(self):
        if bool(self.url) == bool(self.file):
            raise ValidationError("Provide either an audio URL or a recording file.")
        validate_audio_url(self.url)
        if self.is_published and not (
            self.rights_confirmed
            and self.pronunciation_verified
            and self.attribution.strip()
            and self.license_notes.strip()
        ):
            raise ValidationError("Publishing requires recording review and confirmed rights.")
        if not isinstance(self.segments, list):
            raise ValidationError({"segments": "Expected a list of timing segments."})
        for segment in self.segments:
            if not isinstance(segment, dict) or not (
                isinstance(segment.get("start_ms"), int)
                and isinstance(segment.get("end_ms"), int)
                and 0 <= segment["start_ms"] < segment["end_ms"]
            ):
                raise ValidationError({"segments": "Invalid timing segment."})

    @property
    def can_play(self):
        return bool(
            self.is_published
            and self.available
            and self.rights_confirmed
            and self.pronunciation_verified
            and (self.url or self.file)
            and (self.expires_at is None or self.expires_at > timezone.now())
        )

    def __str__(self):
        return self.key


class AudioBinding(TimeStampedModel):
    asset = models.ForeignKey(AudioAsset, on_delete=models.CASCADE, related_name="bindings")
    name = models.ForeignKey(
        "content.NameOfAllah",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audio_bindings",
    )
    passage = models.ForeignKey(
        "content.QuranPassage",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audio_bindings",
    )
    dua = models.ForeignKey(
        "content.Dua",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audio_bindings",
    )
    arabic_item = models.ForeignKey(
        "arabic_learning.ArabicLearningItem",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audio_bindings",
    )
    verse = models.ForeignKey(
        "content.QuranVerse",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audio_bindings",
    )
    word = models.ForeignKey(
        "content.QuranWord",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audio_bindings",
    )
    order = models.PositiveSmallIntegerField(default=1)
    label = models.JSONField(default=dict)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        name__isnull=False,
                        passage__isnull=True,
                        dua__isnull=True,
                        arabic_item__isnull=True,
                        verse__isnull=True,
                        word__isnull=True,
                    )
                    | models.Q(
                        name__isnull=True,
                        passage__isnull=False,
                        dua__isnull=True,
                        arabic_item__isnull=True,
                        verse__isnull=True,
                        word__isnull=True,
                    )
                    | models.Q(
                        name__isnull=True,
                        passage__isnull=True,
                        dua__isnull=False,
                        arabic_item__isnull=True,
                        verse__isnull=True,
                        word__isnull=True,
                    )
                    | models.Q(
                        name__isnull=True,
                        passage__isnull=True,
                        dua__isnull=True,
                        arabic_item__isnull=False,
                        verse__isnull=True,
                        word__isnull=True,
                    )
                    | models.Q(
                        name__isnull=True,
                        passage__isnull=True,
                        dua__isnull=True,
                        arabic_item__isnull=True,
                        verse__isnull=False,
                        word__isnull=True,
                    )
                    | models.Q(
                        name__isnull=True,
                        passage__isnull=True,
                        dua__isnull=True,
                        arabic_item__isnull=True,
                        verse__isnull=True,
                        word__isnull=False,
                    )
                ),
                name="audio_binding_exactly_one_target",
            ),
            *[
                models.UniqueConstraint(
                    fields=["asset", field],
                    condition=models.Q(**{f"{field}__isnull": False}),
                    name=f"unique_audio_{field}",
                )
                for field in ("name", "passage", "dua", "arabic_item", "verse", "word")
            ],
        ]

    def clean(self):
        targets = ("name", "passage", "dua", "arabic_item", "verse", "word")
        if sum(getattr(self, f"{target}_id") is not None for target in targets) != 1:
            raise ValidationError("Bind a recording to exactly one content item.")
        if not isinstance(self.label, dict):
            raise ValidationError({"label": "Expected localized recording labels."})
