from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.db.models import Case, IntegerField, Sum, Value, When
from django.utils import timezone

from .models import (
    FastOperationReceipt,
    PrayerType,
    QadaPrayer,
    QadaProfile,
    QadaSource,
    QadaStatus,
    WorshipEntry,
    WorshipKind,
)

OBLIGATORY_PRAYERS = [
    PrayerType.FAJR,
    PrayerType.DHUHR,
    PrayerType.ASR,
    PrayerType.MAGHRIB,
    PrayerType.ISHA,
]


@dataclass(frozen=True)
class CurrentQada:
    source: str
    prayer_date: object
    prayer_type: str
    prayer_id: int | None = None

    @property
    def key(self):
        if self.source == QadaSource.MANUAL:
            return f"m:{self.prayer_id}"
        return f"h:{self.prayer_date.isoformat()}:{self.prayer_type}"


def _validate_obligatory_prayer(prayer_type):
    if prayer_type not in OBLIGATORY_PRAYERS:
        raise ValueError("Prayer must be one of the five obligatory prayers")


def _previous_prayer(prayer_date, prayer_type):
    index = OBLIGATORY_PRAYERS.index(prayer_type)
    if index == 0:
        return prayer_date - timedelta(days=1), OBLIGATORY_PRAYERS[-1]
    return prayer_date, OBLIGATORY_PRAYERS[index - 1]


@transaction.atomic
def configure_historical_qada(user, start_date, start_prayer):
    _validate_obligatory_prayer(start_prayer)
    if start_date > timezone.localdate():
        raise ValueError("Historical qada start cannot be in the future")
    profile, _ = QadaProfile.objects.select_for_update().get_or_create(user=user)
    if profile.historical_configured:
        if (
            profile.historical_start_date == start_date
            and profile.historical_start_prayer == start_prayer
        ):
            return profile
        raise ValueError("Historical qada is already configured")
    profile.historical_start_date = start_date
    profile.historical_start_prayer = start_prayer
    profile.historical_cursor_date = start_date
    profile.historical_cursor_prayer = start_prayer
    profile.historical_completed = 0
    profile.save()
    return profile


@transaction.atomic
def add_manual_qada(user, prayer_date, prayer_type):
    _validate_obligatory_prayer(prayer_type)
    if prayer_date > timezone.localdate():
        raise ValueError("Missed prayer cannot be in the future")
    profile = QadaProfile.objects.filter(user=user).first()
    if profile and profile.historical_start_date:
        before_start = prayer_date < profile.historical_start_date
        at_or_before_start_prayer = (
            prayer_date == profile.historical_start_date
            and OBLIGATORY_PRAYERS.index(prayer_type)
            <= OBLIGATORY_PRAYERS.index(profile.historical_start_prayer)
        )
        if before_start or at_or_before_start_prayer:
            raise ValueError("Use the historical queue for this prayer")
    prayer, created = QadaPrayer.objects.get_or_create(
        user=user,
        source=QadaSource.MANUAL,
        prayer_date=prayer_date,
        prayer_type=prayer_type,
    )
    return prayer, created


def pending_manual_qada(user):
    prayer_order = Case(
        *[
            When(prayer_type=prayer_type, then=Value(index))
            for index, prayer_type in enumerate(OBLIGATORY_PRAYERS, 1)
        ],
        default=Value(0),
        output_field=IntegerField(),
    )
    return (
        QadaPrayer.objects.filter(user=user, source=QadaSource.MANUAL, status=QadaStatus.PENDING)
        .annotate(prayer_order=prayer_order)
        .order_by("-prayer_date", "-prayer_order", "-created_at")
    )


def current_qada(user):
    manual = pending_manual_qada(user).first()
    if manual:
        return CurrentQada(
            source=QadaSource.MANUAL,
            prayer_date=manual.prayer_date,
            prayer_type=manual.prayer_type,
            prayer_id=manual.id,
        )
    profile = QadaProfile.objects.filter(user=user).first()
    if not profile or not profile.historical_configured:
        return None
    return CurrentQada(
        source=QadaSource.HISTORICAL,
        prayer_date=profile.historical_cursor_date,
        prayer_type=profile.historical_cursor_prayer,
    )


def qada_summary(user):
    profile = QadaProfile.objects.filter(user=user).first()
    return {
        "current": current_qada(user),
        "manual_pending": pending_manual_qada(user).count(),
        "manual_completed": QadaPrayer.objects.filter(
            user=user, source=QadaSource.MANUAL, status=QadaStatus.COMPLETED
        ).count(),
        "historical_completed": profile.historical_completed if profile else 0,
        "historical_configured": bool(profile and profile.historical_configured),
    }


def has_pending_qada(user):
    return current_qada(user) is not None


@transaction.atomic
def complete_current_qada(user, expected_key=None):
    profile, _ = QadaProfile.objects.select_for_update().get_or_create(user=user)
    manual = pending_manual_qada(user).select_for_update().first()
    if manual:
        current = CurrentQada(
            source=QadaSource.MANUAL,
            prayer_date=manual.prayer_date,
            prayer_type=manual.prayer_type,
            prayer_id=manual.id,
        )
        if expected_key and current.key != expected_key:
            raise ValueError("The qada queue has changed")
        manual.status = QadaStatus.COMPLETED
        manual.completed_at = timezone.now()
        manual.save(update_fields=["status", "completed_at", "updated_at"])
    elif profile.historical_configured:
        current = CurrentQada(
            source=QadaSource.HISTORICAL,
            prayer_date=profile.historical_cursor_date,
            prayer_type=profile.historical_cursor_prayer,
        )
        if expected_key and current.key != expected_key:
            raise ValueError("The qada queue has changed")
        QadaPrayer.objects.get_or_create(
            user=user,
            source=QadaSource.HISTORICAL,
            prayer_date=current.prayer_date,
            prayer_type=current.prayer_type,
            defaults={"status": QadaStatus.COMPLETED, "completed_at": timezone.now()},
        )
        next_date, next_prayer = _previous_prayer(current.prayer_date, current.prayer_type)
        profile.historical_cursor_date = next_date
        profile.historical_cursor_prayer = next_prayer
        profile.historical_completed += 1
        profile.save(
            update_fields=[
                "historical_cursor_date",
                "historical_cursor_prayer",
                "historical_completed",
                "updated_at",
            ]
        )
    else:
        raise ValueError("No qada prayer is configured")
    WorshipEntry.objects.create(
        user=user,
        kind=WorshipKind.PRAYER,
        prayer_type=current.prayer_type,
        amount=-1,
        occurred_on=timezone.localdate(),
        note=f"Completed qada {current.source}: {current.prayer_date.isoformat()}",
    )
    return current


def balances_for_user(user):
    rows = (
        WorshipEntry.objects.filter(user=user)
        .values("kind", "prayer_type")
        .annotate(balance=Sum("amount"))
    )
    result = {"fast": 0, "prayers": {value: 0 for value in PrayerType.values}}
    for row in rows:
        balance = max(0, row["balance"] or 0)
        if row["kind"] == WorshipKind.FAST:
            result["fast"] = balance
        elif row["prayer_type"]:
            result["prayers"][row["prayer_type"]] = balance
    return result


@transaction.atomic
def add_debt(user, kind, amount, prayer_type="", note=""):
    if amount <= 0:
        raise ValueError("Debt amount must be positive")
    if kind == WorshipKind.PRAYER and prayer_type not in PrayerType.values:
        raise ValueError("Prayer type is required")
    if kind == WorshipKind.FAST:
        prayer_type = ""
    return WorshipEntry.objects.create(
        user=user,
        kind=kind,
        prayer_type=prayer_type,
        amount=amount,
        occurred_on=timezone.localdate(),
        note=note,
    )


@transaction.atomic
def complete_one(user, kind, prayer_type=""):
    balances = balances_for_user(user)
    current = (
        balances["fast"] if kind == WorshipKind.FAST else balances["prayers"].get(prayer_type, 0)
    )
    if current <= 0:
        raise ValueError("No remaining debt")
    return WorshipEntry.objects.create(
        user=user,
        kind=kind,
        prayer_type=prayer_type if kind == WorshipKind.PRAYER else "",
        amount=-1,
        occurred_on=timezone.localdate(),
        note="Completed via Telegram bot",
    )


@transaction.atomic
def record_fast_operation(user, operation_id, action, amount=1):
    if action not in ("add", "complete") or amount <= 0 or amount > 10000:
        raise ValueError("Invalid fast operation")
    if action == "complete" and amount != 1:
        raise ValueError("Complete one fast at a time")
    existing = FastOperationReceipt.objects.filter(user=user, operation_id=operation_id).first()
    if existing:
        if existing.action != action or existing.amount != amount:
            raise ValueError("This operation ID was already used for another action")
        return existing.entry, False
    entry = (
        add_debt(user, WorshipKind.FAST, amount)
        if action == "add"
        else complete_one(user, WorshipKind.FAST)
    )
    FastOperationReceipt.objects.create(
        user=user, operation_id=operation_id, action=action, amount=amount, entry=entry
    )
    return entry, True
