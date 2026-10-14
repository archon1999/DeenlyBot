import type { WeeklyReport } from './entities';

export function newestReports(reports: WeeklyReport[]) {
  return [...reports].sort((a, b) => b.periodEnd.localeCompare(a.periodEnd) || b.id - a.id);
}

export function reportCount(report: WeeklyReport, key: string) {
  const value = report.data[key];
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : undefined;
}
