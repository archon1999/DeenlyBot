import type { CalendarEvent } from '../entities';

export interface CalendarRepository {
  events(): Promise<CalendarEvent[]>;
}
