import type { StatsDto, ReportsDto } from '../dto';
import type { ProgressStats, ReportsOverview } from '../../domain';

export const mapStats = (d: StatsDto): ProgressStats => ({
  namesTotal: d.names_total,
  namesIntroduced: d.names_introduced,
  namesLearned: d.names_learned,
  namesDue: d.names_due,
  totalAnswers: d.total_answers,
  correctAnswers: d.correct_answers,
  accuracy: d.accuracy,
  arabicLessonsCompleted: d.arabic_lessons_completed,
  arabicLessonsTotal: d.arabic_lessons_total,
  arabicItemsIntroduced: d.arabic_items_introduced,
  arabicDue: d.arabic_due,
  qadaCompleted: d.qada_completed,
});
export const mapReports = (d: ReportsDto): ReportsOverview => ({
  stats: mapStats(d.stats),
  weeklyReports: d.weekly_reports.map((r) => ({
    id: r.id,
    periodStart: r.period_start,
    periodEnd: r.period_end,
    data: r.data,
  })),
});
