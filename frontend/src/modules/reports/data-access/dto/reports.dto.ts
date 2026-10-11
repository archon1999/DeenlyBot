export type StatsDto = {
  names_total: number;
  names_introduced: number;
  names_learned: number;
  names_due: number;
  total_answers: number;
  correct_answers: number;
  accuracy: number;
  arabic_lessons_completed: number;
  arabic_lessons_total: number;
  arabic_items_introduced: number;
  arabic_due: number;
  qada_completed: number;
};
export type ReportsDto = {
  stats: StatsDto;
  weekly_reports: {
    id: number;
    period_start: string;
    period_end: string;
    data: Record<string, number>;
  }[];
};
