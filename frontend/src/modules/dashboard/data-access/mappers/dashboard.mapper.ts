import type { DashboardDto } from '../dto';
import type { DashboardOverview } from '../../domain';

import { mapName } from '../../../names/data-access/mappers';
import { mapQada } from '../../../worship/data-access/mappers';
import { mapLesson } from '../../../arabic/data-access/mappers';
import { mapStats } from '../../../reports/data-access/mappers';
import { mapCalendar } from '../../../calendar/data-access/mappers';

export const mapDashboard = (d: DashboardDto): DashboardOverview => ({
  nextName: d.next_name ? mapName(d.next_name) : null,
  nextArabicLesson: d.next_arabic_lesson ? mapLesson(d.next_arabic_lesson) : null,
  reviewsDue: d.reviews_due,
  arabicReviewsDue: d.arabic_reviews_due,
  stats: mapStats(d.stats),
  qada: mapQada(d.qada),
  upcomingEvents: mapCalendar({ events: d.upcoming_events }),
});
