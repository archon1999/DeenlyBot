from datetime import UTC, date, datetime

import pytest
from hijridate import Gregorian

from apps.islamic_calendar.models import CalendarCorrection, EventTranslation, IslamicEvent
from apps.islamic_calendar.services import add_calendar_months


@pytest.mark.parametrize(
    ("start", "months", "expected"),
    [
        (date(2026, 10, 11), 6, date(2027, 4, 11)),
        (date(2026, 8, 31), 6, date(2027, 2, 28)),
        (date(2023, 8, 31), 6, date(2024, 2, 29)),
    ],
)
def test_six_month_window_uses_calendar_months(start, months, expected):
    assert add_calendar_months(start, months) == expected


@pytest.mark.django_db
def test_dashboard_includes_full_six_month_window_in_profile_timezone(user, monkeypatch):
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    user.timezone = "Asia/Tashkent"
    user.auth_user = get_user_model().objects.create_user(username="calendar-owner", password=None)
    user.save(update_fields=["timezone", "auth_user"])
    monkeypatch.setattr(
        "apps.api.dto.timezone.now", lambda: datetime(2026, 10, 10, 23, 30, tzinfo=UTC)
    )
    today = date(2026, 10, 11)
    hijri_year = Gregorian(today.year, today.month, today.day).to_hijri().year
    dates = [date(2026, 10, 10), today, date(2027, 4, 11), date(2027, 4, 12)]
    for index, event_date in enumerate(dates):
        event = IslamicEvent.objects.create(slug=f"window-{index}", hijri_month=1, hijri_day=1)
        EventTranslation.objects.create(event=event, language=user.language, title=f"Date {index}")
        CalendarCorrection.objects.create(
            event=event, hijri_year=hijri_year, region="global", gregorian_date=event_date
        )
    client = APIClient()
    client.force_login(user.auth_user)
    response = client.get("/api/v1/dashboard/")
    assert response.status_code == 200
    assert [event["date"] for event in response.json()["upcoming_events"]] == [
        "2026-10-11",
        "2027-04-11",
    ]
