export type SettingsDto = {
  language: 'uz' | 'ru' | 'en';
  timezone: string;
  enabled: boolean;
  random_messages_per_day: number;
  random_window_start: string;
  random_window_end: string;
  weekly_report_enabled: boolean;
  weekly_report_weekday: number;
  weekly_report_time: string;
};
