import hashlib
import hmac
import json
import secrets
import uuid
from datetime import timedelta
from urllib.parse import parse_qsl

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.users.models import TelegramUser

from .account_services import reconcile_telegram_profile
from .authentication import telegram_access_allowed
from .models import BrowserLoginChallenge

CHALLENGE_TTL_SECONDS = 300
MINIAPP_MAX_AGE_SECONDS = 600


def _digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


@transaction.atomic
def create_browser_challenge(session, *, purpose="login", account=None):
    previous = session.get("telegram_login_challenge")
    if previous:
        BrowserLoginChallenge.objects.filter(id=previous, consumed_at__isnull=True).update(
            consumed_at=timezone.now()
        )
    token = secrets.token_hex(24)
    binding = secrets.token_urlsafe(32)
    challenge = BrowserLoginChallenge.objects.create(
        token_hash=_digest(token),
        browser_binding_hash=_digest(binding),
        expires_at=timezone.now() + timedelta(seconds=CHALLENGE_TTL_SECONDS),
        purpose=purpose,
        requested_by=account if purpose == "link" else None,
    )
    session["telegram_login_challenge"] = str(challenge.id)
    session["telegram_login_binding"] = binding
    return challenge, token


def inspect_browser_challenge(token, profile):
    if not telegram_access_allowed(profile):
        raise ValueError("Only the active personal owner can approve this login")
    challenge = (
        BrowserLoginChallenge.objects.select_related("requested_by")
        .filter(token_hash=_digest(token))
        .first()
    )
    if not challenge or challenge.expires_at <= timezone.now() or challenge.consumed_at:
        raise ValueError("Login request has expired or was already used")
    if challenge.approved_by_id and challenge.approved_by_id != profile.id:
        raise ValueError("Login request belongs to another account")
    return challenge


@transaction.atomic
def approve_browser_challenge(token, profile, *, link_consent=False, login_consent=False):
    challenge = inspect_browser_challenge(token, profile)
    if challenge.purpose == "link" and not link_consent:
        raise ValueError("Telegram linking requires explicit confirmation")
    if link_consent and challenge.purpose != "link":
        raise ValueError("Incorrect request purpose")
    if challenge.purpose == "login" and not login_consent:
        raise ValueError("Browser login requires explicit confirmation")
    if login_consent and challenge.purpose != "login":
        raise ValueError("Incorrect request purpose")
    challenge.approved_by = profile
    challenge.approved_at = challenge.approved_at or timezone.now()
    challenge.save(update_fields=["approved_by", "approved_at", "updated_at"])
    return challenge


def _bound_auth_user(profile):
    # Called inside the same short write transaction as challenge consumption.
    if profile.auth_user_id:
        account = profile.auth_user
        if not account.is_active:
            raise ValueError("This account has been disabled")
        return account
    account = get_user_model().objects.create_user(
        username=f"telegram_{uuid.uuid4().hex}",
        first_name=profile.first_name[:150],
        last_name=profile.last_name[:150],
        password=None,
    )
    profile.auth_user = account
    profile.save(update_fields=["auth_user", "updated_at"])
    return account


@transaction.atomic
def consume_browser_challenge(session, *, purpose="login", account=None):
    challenge_id = session.get("telegram_login_challenge")
    binding = session.get("telegram_login_binding", "")
    if not challenge_id or not binding:
        raise ValueError("Start a new login request in this browser")
    challenge = (
        BrowserLoginChallenge.objects.select_for_update(of=("self",))
        .select_related("approved_by__auth_user")
        .filter(id=challenge_id)
        .first()
    )
    if (
        not challenge
        or not hmac.compare_digest(challenge.browser_binding_hash, _digest(binding))
        or challenge.expires_at <= timezone.now()
        or challenge.consumed_at
        or challenge.purpose != purpose
        or (purpose == "link" and challenge.requested_by_id != getattr(account, "pk", None))
    ):
        raise ValueError("Login request has expired or was already used")
    if not challenge.approved_by_id:
        return None
    profile = challenge.approved_by
    if not telegram_access_allowed(profile):
        raise ValueError("This Telegram profile is not allowed to sign in")
    if purpose == "link":
        target = (
            TelegramUser.objects.select_for_update(of=("self",))
            .select_related("auth_user")
            .get(auth_user=account, is_active=True)
        )
        profile = reconcile_telegram_profile(target, profile)
    else:
        account = _bound_auth_user(profile)
    challenge.consumed_at = timezone.now()
    challenge.save(update_fields=["consumed_at", "updated_at"])
    session.pop("telegram_login_challenge", None)
    session.pop("telegram_login_binding", None)
    return account, profile


def verified_miniapp_telegram_id(init_data):
    """Verify Telegram's raw query string, never client-provided initDataUnsafe."""
    if not settings.BOT_TOKEN:
        raise ValueError("Telegram authentication is not configured")
    try:
        pairs = parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
        data = dict(pairs)
        if len(pairs) != len(data):
            raise ValueError("Duplicate Telegram authentication fields")
        supplied_hash = data.pop("hash")
        check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
        secret = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected_hash = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_hash, supplied_hash):
            raise ValueError("Invalid Telegram authentication signature")
        auth_date = int(data["auth_date"])
        age = timezone.now().timestamp() - auth_date
        if age < -30 or age > MINIAPP_MAX_AGE_SECONDS:
            raise ValueError("Telegram authentication has expired")
        user_data = json.loads(data["user"])
        telegram_id = user_data["id"]
        if isinstance(telegram_id, bool) or not isinstance(telegram_id, int) or telegram_id <= 0:
            raise ValueError("Invalid Telegram user")
        return telegram_id
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid Telegram authentication data") from exc


@transaction.atomic
def miniapp_account(init_data):
    telegram_id = verified_miniapp_telegram_id(init_data)
    profile = TelegramUser.objects.select_for_update().filter(telegram_id=telegram_id).first()
    if not telegram_access_allowed(profile):
        raise ValueError("This Telegram profile is not allowed to sign in")
    return _bound_auth_user(profile), profile
