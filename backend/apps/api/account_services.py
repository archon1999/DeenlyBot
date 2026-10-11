import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException, ValidationError

from apps.users.models import AccountCredential, AccountKind, NotificationPreference, TelegramUser

from .authentication import profile_allowed


class AccountConflict(APIException):
    status_code = 409
    default_code = "account_conflict"


def _profile_for_account(account):
    profile = TelegramUser.objects.select_related("auth_user").filter(auth_user=account).first()
    return profile if profile_allowed(profile) else None


@transaction.atomic
def create_guest(account=None, *, language="uz", timezone="Asia/Tashkent"):
    if account and account.is_authenticated:
        profile = _profile_for_account(account)
        if not profile:
            raise ValueError("This account is not active")
        return account, profile
    account = get_user_model().objects.create_user(
        username=f"guest_{uuid.uuid4().hex}", password=None
    )
    profile = TelegramUser.objects.create(
        auth_user=account, account_kind=AccountKind.GUEST, language=language, timezone=timezone
    )
    NotificationPreference.objects.create(user=profile, enabled=False, weekly_report_enabled=False)
    return account, profile


def register_account(*, email, password, first_name, account=None, language=None):
    try:
        return _register_account(
            email=email,
            password=password,
            first_name=first_name,
            account=account,
            language=language,
        )
    except IntegrityError:
        # A concurrent request may win after the initial existence check. The
        # inner atomic/savepoint has rolled back before checking the winner.
        if AccountCredential.objects.filter(email__iexact=email.strip().casefold()).exists():
            raise ValidationError({"email": "An account with this email already exists"}) from None
        raise


@transaction.atomic
def _register_account(*, email, password, first_name, account=None, language=None):
    email = email.strip().casefold()
    if (
        AccountCredential.objects.filter(email__iexact=email).exists()
        or get_user_model()
        .objects.filter(email__iexact=email)
        .exclude(pk=getattr(account, "pk", None))
        .exists()
    ):
        raise ValidationError({"email": "An account with this email already exists"})
    if account and account.is_authenticated:
        account = get_user_model().objects.select_for_update().get(pk=account.pk)
        profile = _profile_for_account(account)
        if not profile:
            raise ValueError("This account is not active")
        if AccountCredential.objects.filter(user=account).exists() or account.has_usable_password():
            raise ValueError("This account already has login credentials")
    else:
        account = get_user_model()(username=f"member_{uuid.uuid4().hex}")
        profile = None
    account.email = email
    account.first_name = first_name
    try:
        validate_password(password, user=account)
    except DjangoValidationError as exc:
        raise ValidationError({"password": exc.messages}) from exc
    account.set_password(password)
    account.save()
    AccountCredential.objects.create(user=account, email=email)
    if profile is None:
        profile = TelegramUser.objects.create(
            auth_user=account,
            account_kind=AccountKind.MEMBER,
            first_name=first_name,
            first_name_customized=True,
            language=language or "uz",
        )
        NotificationPreference.objects.create(
            user=profile, enabled=False, weekly_report_enabled=False
        )
    else:
        profile.auth_user = account
        profile.account_kind = AccountKind.MEMBER
        profile.first_name = first_name
        profile.first_name_customized = True
        if language:
            profile.language = language
        profile.save(
            update_fields=[
                "account_kind",
                "first_name",
                "first_name_customized",
                "language",
                "updated_at",
            ]
        )
    return account, profile


def credential_account(email, password):
    credential = (
        AccountCredential.objects.select_related("user")
        .filter(email=email.strip().casefold())
        .first()
    )
    if credential is None:
        # Keep password hashing work comparable for unknown emails.
        get_user_model()().set_password(password)
        raise ValueError("Email or password is incorrect")
    account = credential.user
    valid_password = account.check_password(password)
    profile = _profile_for_account(account)
    if not valid_password or not account.is_active or not profile:
        raise ValueError("Email or password is incorrect")
    return account, profile


@transaction.atomic
def update_account_profile(profile, changes):
    profile = TelegramUser.objects.select_for_update().get(pk=profile.pk)
    if "first_name" in changes:
        profile.first_name = changes["first_name"]
        profile.first_name_customized = True
        profile.save(update_fields=["first_name", "first_name_customized", "updated_at"])
        profile.auth_user.first_name = profile.first_name
        profile.auth_user.save(update_fields=["first_name"])
    settings_changes = {
        key: value for key, value in changes.items() if key in ("language", "timezone")
    }
    if settings_changes:
        from apps.users.services import update_platform_settings

        profile, _ = update_platform_settings(profile, settings_changes)
    return profile


def _has_progress(profile):
    from apps.arabic_learning.models import (
        ArabicQuizQuestion,
        UserArabicItemProgress,
        UserArabicLessonProgress,
    )
    from apps.content.models import Favorite
    from apps.islamic_calendar.models import EventSubscription
    from apps.learning.models import QuizQuestion, UserNameProgress
    from apps.library_learning.models import LibraryQuizQuestion, UserLibraryProgress
    from apps.notifications.models import WeeklyReport
    from apps.worship.models import QadaPrayer, QadaProfile, WorshipEntry

    models = (
        UserNameProgress,
        QuizQuestion,
        UserArabicLessonProgress,
        UserArabicItemProgress,
        ArabicQuizQuestion,
        UserLibraryProgress,
        LibraryQuizQuestion,
        Favorite,
        EventSubscription,
        WeeklyReport,
        QadaPrayer,
        WorshipEntry,
    )
    return (
        any(model.objects.filter(user=profile).exists() for model in models)
        or QadaProfile.objects.filter(user=profile, historical_start_date__isnull=False).exists()
    )


@transaction.atomic
def reconcile_telegram_profile(target, verified):
    """Keep the profile with progress. Never merge two independent histories or credentials."""
    from apps.notifications.models import NotificationStatus, ScheduledNotification

    if target.pk == verified.pk:
        return target
    if target.telegram_id and target.telegram_id != verified.telegram_id:
        raise AccountConflict(
            {
                "code": "telegram_already_linked",
                "detail": "This account already has another Telegram identity linked.",
            }
        )
    old_account = verified.auth_user if verified.auth_user_id else None
    if old_account and not old_account.is_active:
        raise AccountConflict(
            {
                "code": "disabled_telegram_account",
                "detail": "This Telegram account is disabled and cannot be transferred.",
            }
        )
    if old_account and (
        old_account.has_usable_password()
        or AccountCredential.objects.filter(user=old_account).exists()
    ):
        raise AccountConflict(
            {
                "code": "registered_telegram_account",
                "detail": "This Telegram identity belongs to an existing registered account. Sign in to that account; it cannot be transferred.",
            }
        )
    target_progress, verified_progress = _has_progress(target), _has_progress(verified)
    if target_progress and verified_progress:
        raise AccountConflict(
            {
                "code": "both_profiles_have_progress",
                "detail": "Both accounts have progress. No data was changed. Sign in with Telegram and add email credentials there, or keep the accounts separate.",
            }
        )
    account = target.auth_user
    if verified_progress:
        # The empty website profile is retired, retaining its FKs; the legacy profile survives.
        target.auth_user = None
        target.is_active = False
        target.save(update_fields=["auth_user", "is_active", "updated_at"])
        verified.auth_user = account
        verified.account_kind = target.account_kind
        verified.first_name = target.first_name or verified.first_name
        verified.first_name_customized = target.first_name_customized
        verified.language = target.language
        verified.timezone = target.timezone
        verified.save()
        winner, retired = verified, target
    else:
        # The empty Telegram profile is retired; all website progress stays on its original ID.
        telegram_id, username, owner = verified.telegram_id, verified.username, verified.is_owner
        verified.telegram_id = None
        verified.is_owner = False
        verified.is_active = False
        verified.auth_user = None
        verified.save(
            update_fields=["telegram_id", "is_owner", "is_active", "auth_user", "updated_at"]
        )
        target.telegram_id = telegram_id
        target.username = username
        target.is_owner = owner
        target.save(update_fields=["telegram_id", "username", "is_owner", "updated_at"])
        winner, retired = target, verified
    if old_account and old_account.pk != account.pk:
        old_account.is_active = False
        old_account.save(update_fields=["is_active"])
    ScheduledNotification.objects.filter(user=retired, status=NotificationStatus.PENDING).update(
        status=NotificationStatus.SKIPPED
    )
    preference, _ = NotificationPreference.objects.get_or_create(user=winner)
    preference.schedule_version += 1
    preference.save(update_fields=["schedule_version", "updated_at"])

    def replan():
        from apps.notifications.models import NotificationKind
        from apps.notifications.services import (
            plan_event_reminders_for_user,
            replan_daily_for_user,
            replan_weekly_for_user,
        )

        refreshed = TelegramUser.objects.select_related("notification_preferences").get(
            pk=winner.pk
        )
        ScheduledNotification.objects.filter(
            user=refreshed,
            status=NotificationStatus.PENDING,
            dedupe_key__startswith=f"daily:{refreshed.pk}:",
        ).update(status=NotificationStatus.SKIPPED)
        ScheduledNotification.objects.filter(
            user=refreshed, status=NotificationStatus.PENDING, kind=NotificationKind.EVENT
        ).update(status=NotificationStatus.SKIPPED)
        replan_daily_for_user(refreshed)
        replan_weekly_for_user(refreshed)
        plan_event_reminders_for_user(refreshed)

    transaction.on_commit(replan)
    return winner
