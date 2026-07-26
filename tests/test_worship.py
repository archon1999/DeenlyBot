import pytest

from apps.worship.models import PrayerType, WorshipKind
from apps.worship.services import add_debt, balances_for_user, complete_one


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
