from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import PrayerType, WorshipEntry, WorshipKind


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
