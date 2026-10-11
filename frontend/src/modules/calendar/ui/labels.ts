import { useLocale } from 'src/shared/i18n';

const labels = {
  uz: {
    title: 'Islomiy taqvim',
    subtitle: 'Yil davomida muhim sanalar va eslatmalar.',
    next: 'Eng yaqin sana',
    upcoming: 'Yaqinlashayotgan sanalar',
    dates: 'muhim sana',
    estimated: 'Taxminiy sana',
    hijri: 'hijriy yil',
    empty: 'Hozircha taqvimda tadbirlar yo‘q.',
    hint: 'Hijriy sanalar oy ko‘rinishi va mahalliy e’longa ko‘ra farq qilishi mumkin.',
  },
  ru: {
    title: 'Исламский календарь',
    subtitle: 'Важные даты и напоминания в течение года.',
    next: 'Ближайшая дата',
    upcoming: 'Предстоящие даты',
    dates: 'важных дат',
    estimated: 'Предварительная дата',
    hijri: 'год хиджры',
    empty: 'В календаре пока нет событий.',
    hint: 'Даты хиджры могут отличаться в зависимости от наблюдения луны и местных объявлений.',
  },
  en: {
    title: 'Islamic calendar',
    subtitle: 'Important dates and reminders throughout the year.',
    next: 'Next important date',
    upcoming: 'Upcoming dates',
    dates: 'important dates',
    estimated: 'Estimated date',
    hijri: 'Hijri year',
    empty: 'There are no calendar events yet.',
    hint: 'Hijri dates may vary with moon sightings and local announcements.',
  },
};
export const useCalendarLabels = () => labels[useLocale().language];
export type CalendarLabels = ReturnType<typeof useCalendarLabels>;
