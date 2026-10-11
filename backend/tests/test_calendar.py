from datetime import date

import pytest
from django.core.management import call_command
from hijridate import Hijri

from apps.islamic_calendar.models import CalendarCorrection, EventTranslation, IslamicEvent
from apps.islamic_calendar.services import occurrence_date, upcoming_events


@pytest.mark.django_db
def test_upcoming_hijri_event_and_manual_correction():
    current = Hijri.today()
    event = IslamicEvent.objects.create(
        slug="test-event",
        hijri_month=current.month,
        hijri_day=current.day,
        requires_local_confirmation=True,
        reminder_days=[1],
    )
    EventTranslation.objects.create(event=event, language="ru", title="Событие")
    calculated, estimated = occurrence_date(event, current.year)
    assert estimated is True

    corrected = date(calculated.year, calculated.month, calculated.day)
    CalendarCorrection.objects.create(
        event=event, hijri_year=current.year, gregorian_date=corrected
    )
    assert occurrence_date(event, current.year) == (corrected, False)
    assert upcoming_events("ru", from_date=corrected, days=1)[0].title == "Событие"


@pytest.mark.django_db
def test_seeded_calendar_has_an_event_within_full_hijri_cycle():
    call_command("seed_content", verbosity=0)

    assert upcoming_events("ru", from_date=date.today(), days=400)
