import type { AllahName } from '../../../names';
import type { ArabicLesson } from '../../../arabic';
import type { QadaSummary } from '../../../worship';
import type { ProgressStats } from '../../../reports';
import type { CalendarEvent } from '../../../calendar';

export type DashboardOverview = {
  nextName: AllahName | null;
  nextArabicLesson: ArabicLesson | null;
  reviewsDue: number;
  arabicReviewsDue: number;
  stats: ProgressStats;
  qada: QadaSummary;
  upcomingEvents: CalendarEvent[];
};
