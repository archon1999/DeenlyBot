import type { NavSectionProps } from 'src/shared/ui/nav-section';

import { useLocale } from 'src/shared/i18n';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

const labels = {
  uz: {
    learning: 'Har kungi o‘rganish',
    personal: 'Shaxsiy maydon',
    names: 'Allohning ismlari',
    arabic: 'Arab tili',
    library: 'Kutubxona',
    qada: 'Qazo',
    calendar: 'Taqvim',
    reports: 'Hisobotlar',
  },
  ru: {
    learning: 'Ежедневное обучение',
    personal: 'Личное пространство',
    names: 'Имена Аллаха',
    arabic: 'Арабский язык',
    library: 'Библиотека',
    qada: 'Када',
    calendar: 'Календарь',
    reports: 'Отчёты',
  },
  en: {
    learning: 'Daily learning',
    personal: 'Personal space',
    names: 'Names of Allah',
    arabic: 'Arabic',
    library: 'Library',
    qada: 'Qada',
    calendar: 'Calendar',
    reports: 'Reports',
  },
};
export function useNavData(): NavSectionProps['data'] {
  const { language } = useLocale();
  const t = labels[language];
  return [
    {
      subheader: t.learning,
      items: [
        { title: t.names, path: '/names', icon: <OutlineIcon name="names" /> },
        { title: t.arabic, path: '/arabic', icon: <OutlineIcon name="arabic" /> },
        { title: t.library, path: '/library', icon: <OutlineIcon name="library" /> },
      ],
    },
    {
      subheader: t.personal,
      items: [
        {
          title: t.qada,
          path: '/qada',
          icon: <OutlineIcon name="qada" />,
        },
        { title: t.calendar, path: '/calendar', icon: <OutlineIcon name="calendar" /> },
        { title: t.reports, path: '/reports', icon: <OutlineIcon name="reports" /> },
      ],
    },
  ];
}
