import type { CalendarDto } from '../dto';
import type { CalendarEvent } from '../../domain';

export const mapCalendar = (d: CalendarDto): CalendarEvent[] =>
  d.events.map((e) => ({
    id: e.id,
    date: e.date,
    hijriYear: e.hijri_year,
    title: e.title,
    description: e.description,
    isEstimated: e.is_estimated,
  }));
