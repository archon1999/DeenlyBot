import type { NameDto } from '../../../names/data-access/dto';
import type { LessonDto } from '../../../arabic/data-access/dto';
import type { StatsDto } from '../../../reports/data-access/dto';
import type { CalendarDto } from '../../../calendar/data-access/dto';
import type { QadaSummaryDto } from '../../../worship/data-access/dto';

export type DashboardDto = {
  next_name: NameDto | null;
  next_arabic_lesson: LessonDto | null;
  reviews_due: number;
  arabic_reviews_due: number;
  stats: StatsDto;
  qada: QadaSummaryDto;
  upcoming_events: CalendarDto['events'];
};
