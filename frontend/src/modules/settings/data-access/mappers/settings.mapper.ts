import type { SettingsDto } from '../dto';
import type { UserSettings } from '../../domain';

export const mapSettings = (d: SettingsDto): UserSettings => ({
  language: d.language,
  timezone: d.timezone,
  enabled: d.enabled,
  randomMessagesPerDay: d.random_messages_per_day,
  randomWindowStart: d.random_window_start,
  randomWindowEnd: d.random_window_end,
  weeklyReportEnabled: d.weekly_report_enabled,
  weeklyReportWeekday: d.weekly_report_weekday,
  weeklyReportTime: d.weekly_report_time,
});
export const settingsPayload = (p: UserSettings): SettingsDto => ({
  language: p.language,
  timezone: p.timezone,
  enabled: p.enabled,
  random_messages_per_day: p.randomMessagesPerDay,
  random_window_start: p.randomWindowStart,
  random_window_end: p.randomWindowEnd,
  weekly_report_enabled: p.weeklyReportEnabled,
  weekly_report_weekday: p.weeklyReportWeekday,
  weekly_report_time: p.weeklyReportTime,
});
