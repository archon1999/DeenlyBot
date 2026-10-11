from datetime import date

import pytest

from apps.worship.models import PrayerType, QadaSource, QadaStatus, WorshipKind
from apps.worship.services import (
    add_debt,
    add_manual_qada,
    balances_for_user,
    complete_current_qada,
    complete_one,
    configure_historical_qada,
    current_qada,
    qada_summary,
)


@pytest.mark.django_db
def test_qada_is_an_auditable_ledger(user):
    add_debt(user, WorshipKind.PRAYER, 3, PrayerType.FAJR, "Initial balance")
    complete_one(user, WorshipKind.PRAYER, PrayerType.FAJR)
    add_debt(user, WorshipKind.FAST, 2)
    complete_one(user, WorshipKind.FAST)

    balances = balances_for_user(user)
    assert balances["prayers"][PrayerType.FAJR] == 2
    assert balances["fast"] == 1
    assert user.worship_entries.count() == 4


@pytest.mark.django_db
def test_cannot_complete_empty_debt(user):
    with pytest.raises(ValueError, match="No remaining debt"):
        complete_one(user, WorshipKind.FAST)


@pytest.mark.django_db
def test_invalid_prayer_type_is_rejected(user):
    with pytest.raises(ValueError, match="Prayer type"):
        add_debt(user, WorshipKind.PRAYER, 1, "invalid")


@pytest.mark.django_db
def test_historical_qada_moves_back_in_required_prayer_order(user):
    configure_historical_qada(user, date(2026, 5, 23), PrayerType.FAJR)

    first = current_qada(user)
    assert (first.source, first.prayer_date, first.prayer_type) == (
        QadaSource.HISTORICAL,
        date(2026, 5, 23),
        PrayerType.FAJR,
    )

    complete_current_qada(user, first.key)
    second = current_qada(user)
    assert (second.prayer_date, second.prayer_type) == (
        date(2026, 5, 22),
        PrayerType.ISHA,
    )

    complete_current_qada(user, second.key)
    third = current_qada(user)
    assert (third.prayer_date, third.prayer_type) == (
        date(2026, 5, 22),
        PrayerType.MAGHRIB,
    )
    assert qada_summary(user)["historical_completed"] == 2


@pytest.mark.django_db
def test_manual_qada_has_priority_and_is_newest_first(user):
    configure_historical_qada(user, date(2026, 5, 23), PrayerType.FAJR)
    fajr, _ = add_manual_qada(user, date(2026, 7, 27), PrayerType.FAJR)
    isha, _ = add_manual_qada(user, date(2026, 7, 27), PrayerType.ISHA)
    add_manual_qada(user, date(2026, 7, 26), PrayerType.DHUHR)

    assert current_qada(user).prayer_id == isha.id
    complete_current_qada(user, current_qada(user).key)
    assert current_qada(user).prayer_id == fajr.id
    complete_current_qada(user, current_qada(user).key)
    assert current_qada(user).prayer_date == date(2026, 7, 26)

    assert (
        user.qada_prayers.filter(source=QadaSource.MANUAL, status=QadaStatus.COMPLETED).count() == 2
    )


@pytest.mark.django_db
def test_qada_rejects_witr_duplicates_and_stale_confirmation(user):
    configure_historical_qada(user, date(2026, 5, 23), PrayerType.FAJR)
    with pytest.raises(ValueError, match="five obligatory"):
        add_manual_qada(user, date(2026, 7, 27), PrayerType.WITR)

    prayer, created = add_manual_qada(user, date(2026, 7, 27), PrayerType.DHUHR)
    duplicate, duplicate_created = add_manual_qada(user, date(2026, 7, 27), PrayerType.DHUHR)
    assert created is True
    assert duplicate_created is False
    assert duplicate.id == prayer.id

    with pytest.raises(ValueError, match="queue has changed"):
        complete_current_qada(user, "m:999999")
