type DateLanguage = 'uz' | 'ru' | 'en';
type DateParts = { day: string; month: string; year: string };

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

export function formatDateParts(dateString: string, language: DateLanguage): DateParts {
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
