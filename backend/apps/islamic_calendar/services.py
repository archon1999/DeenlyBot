from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta

from hijridate import Gregorian, Hijri

from .models import CalendarCorrection, IslamicEvent


@dataclass(frozen=True)
class EventOccurrence:
    event: IslamicEvent
    date: date
    hijri_year: int
    title: str
    description: str
    is_estimated: bool


def add_calendar_months(value, months):
    month_index = value.year * 12 + value.month - 1 + months
    year, month = divmod(month_index, 12)
    month += 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def localized_event(event, language):
    return (
        event.translations.filter(language=language).first()
        or event.translations.filter(language="ru").first()
    )


def occurrence_date(event, hijri_year, region="global"):
    correction = CalendarCorrection.objects.filter(
        event=event, hijri_year=hijri_year, region=region
    ).first()
    if correction:
        return correction.gregorian_date, False
    converted = Hijri(hijri_year, event.hijri_month, event.hijri_day).to_gregorian()
    return date(converted.year, converted.month, converted.day), event.requires_local_confirmation


def upcoming_events(language, from_date=None, days=400, region="global"):
    from_date = from_date or date.today()
    until = from_date + timedelta(days=days)
    current_hijri = Gregorian(from_date.year, from_date.month, from_date.day).to_hijri()
    result = []
    for event in IslamicEvent.objects.filter(is_published=True).prefetch_related("translations"):
        for year in (current_hijri.year, current_hijri.year + 1, current_hijri.year + 2):
            event_date, is_estimated = occurrence_date(event, year, region)
            if from_date <= event_date <= until:
                translation = localized_event(event, language)
                result.append(
                    EventOccurrence(
                        event,
                        event_date,
                        year,
                        translation.title,
                        translation.description,
                        is_estimated,
                    )
                )
                break
    return sorted(result, key=lambda item: item.date)
