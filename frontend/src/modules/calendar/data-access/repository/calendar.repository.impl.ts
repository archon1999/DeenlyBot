import type { CalendarDto } from '../dto';
import type { CalendarRepository } from '../../domain';

import { apiClient } from 'src/shared/api';

import { mapCalendar } from '../mappers';

export const calendarRepository: CalendarRepository = {
  events: async () => mapCalendar(await apiClient.get<CalendarDto>('calendar/')),
};
