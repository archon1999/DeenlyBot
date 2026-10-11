from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission

from apps.users.models import TelegramUser


def owner_allowed(profile):
    return bool(
        profile
        and profile.is_active
        and profile.is_owner
        and (
            not settings.BOT_OWNER_TELEGRAM_ID
            or profile.telegram_id == settings.BOT_OWNER_TELEGRAM_ID
        )
    )


def profile_allowed(profile):
    return bool(
        profile and profile.is_active and profile.auth_user_id and profile.auth_user.is_active
    )


def telegram_access_allowed(profile):
    return bool(
        profile
        and profile.is_active
        and profile.telegram_id
        and (not settings.PERSONAL_BOT_MODE or owner_allowed(profile))
    )


class CsrfSessionAuthentication(SessionAuthentication):
    """Login endpoints need CSRF protection even before a user is authenticated."""

    def authenticate(self, request):
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            self.enforce_csrf(request)
        return super().authenticate(request)


class IsActiveProfile(BasePermission):
    message = "Sign in to an active account to continue."

    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.is_active:
            return False
        profile = TelegramUser.objects.filter(auth_user=request.user).first()
        if not profile_allowed(profile):
            return False
        request.profile = profile
        return True
