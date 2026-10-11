import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.users.models import TelegramUser


class BrowserLoginChallenge(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_hash = models.CharField(max_length=64, unique=True)
    browser_binding_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField(db_index=True)
    purpose = models.CharField(
        max_length=8, choices=[("login", "Login"), ("link", "Link")], default="login"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    approved_by = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def verification_code(self):
        return self.token_hash[:6].upper()
