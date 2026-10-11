type CalendarLanguage = 'uz' | 'ru' | 'en';
type CalendarDateParts = { day: string; month: string; year: string };

const uzbekMonths = [
  'yanvar',
  'fevral',
  'mart',
  'aprel',
  'may',
  'iyun',
  'iyul',
  'avgust',
  'sentabr',
  'oktabr',
  'noyabr',
  'dekabr',
] as const;

export function formatCalendarDate(
  dateString: string,
  language: CalendarLanguage
): CalendarDateParts {
  const date = new Date(`${dateString}T12:00:00Z`);
  if (Number.isNaN(date.getTime())) return { day: '—', month: '—', year: '—' };
  const month =
    language === 'uz'
      ? uzbekMonths[date.getUTCMonth()]
      : new Intl.DateTimeFormat(language === 'ru' ? 'ru-RU' : 'en-US', {
          month: 'short',
          timeZone: 'UTC',
        }).format(date);
  return { day: String(date.getUTCDate()), month, year: String(date.getUTCFullYear()) };
}
