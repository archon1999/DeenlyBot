export type UserLanguage = 'uz' | 'ru' | 'en';
export type UserSettings = {
  language: UserLanguage;
  timezone: string;
  enabled: boolean;
  randomMessagesPerDay: number;
  randomWindowStart: string;
  randomWindowEnd: string;
  weeklyReportEnabled: boolean;
  weeklyReportWeekday: number;
  weeklyReportTime: string;
};
