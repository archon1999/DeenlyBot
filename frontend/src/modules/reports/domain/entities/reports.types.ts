export type ProgressStats = {
  namesTotal: number;
  namesIntroduced: number;
  namesLearned: number;
  namesDue: number;
  totalAnswers: number;
  correctAnswers: number;
  accuracy: number;
  arabicLessonsCompleted: number;
  arabicLessonsTotal: number;
  arabicItemsIntroduced: number;
  arabicDue: number;
  qadaCompleted: number;
};
export type WeeklyReport = {
  id: number;
  periodStart: string;
  periodEnd: string;
  data: Record<string, number>;
};
export type ReportsOverview = { stats: ProgressStats; weeklyReports: WeeklyReport[] };
