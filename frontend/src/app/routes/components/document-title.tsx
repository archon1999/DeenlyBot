import type { Language } from 'src/shared/i18n';

import { useEffect } from 'react';
import { useLocation } from 'react-router';

import { useLocale } from 'src/shared/i18n';
import { failureLabels } from 'src/shared/ui/failure-page';

export const pageTitleLabels = {
  uz: {
    dashboard: 'Allohning ismlari, arab tili va duolar',
    names: 'Allohning ismlari',
    arabic: 'Arab tili',
    library: 'Kutubxona',
    qada: 'Qazo',
    calendar: 'Taqvim',
    reports: 'Hisobotlar',
    settings: 'Sozlamalar',
    profile: 'Mening profilim',
    login: 'Kirish',
    register: 'Akkaunt yaratish',
    notFound: failureLabels.uz.notFound,
  },
  ru: {
    dashboard: 'Имена Аллаха, арабский язык и дуа',
    names: 'Имена Аллаха',
    arabic: 'Арабский язык',
    library: 'Библиотека',
    qada: 'Када',
    calendar: 'Календарь',
    reports: 'Отчёты',
    settings: 'Настройки',
    profile: 'Мой профиль',
    login: 'Войти',
    register: 'Создать аккаунт',
    notFound: failureLabels.ru.notFound,
  },
  en: {
    dashboard: 'Names of Allah, Arabic and duas',
    names: 'Names of Allah',
    arabic: 'Arabic',
    library: 'Library',
    qada: 'Qada',
    calendar: 'Calendar',
    reports: 'Reports',
    settings: 'Settings',
    profile: 'My profile',
    login: 'Sign in',
    register: 'Create account',
    notFound: failureLabels.en.notFound,
  },
} as const;

type PageTitleKey = keyof (typeof pageTitleLabels)['uz'];

const titleByPath: Readonly<Record<string, PageTitleKey>> = {
  '/': 'dashboard',
  '/names': 'names',
  '/arabic': 'arabic',
  '/library': 'library',
  '/qada': 'qada',
  '/worship': 'qada',
  '/calendar': 'calendar',
  '/reports': 'reports',
  '/settings': 'settings',
  '/profile': 'profile',
  '/login': 'login',
};

/** Match the actual router paths; unknown nested URLs remain 404 rather than feature titles. */
export function getPageTitle(pathname: string, search: string, language: Language): string {
  const path = pathname.replace(/\/+$/, '').toLowerCase() || '/';
  const page = titleByPath[path] ?? 'notFound';
  const key =
    page === 'login' && new URLSearchParams(search).get('mode') === 'register' ? 'register' : page;
  return `${pageTitleLabels[language][key]} | Deenly.uz`;
}

export function DocumentTitle() {
  const { pathname, search } = useLocation();
  const { language } = useLocale();

  useEffect(() => {
    document.title = getPageTitle(pathname, search, language);
    const canonical = document.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (canonical) canonical.href = `https://deenly.uz${pathname}`;
    const robots = document.querySelector<HTMLMetaElement>('meta[name="robots"]');
    if (robots) robots.content = pathname === '/' ? 'index,follow,max-image-preview:large' : 'noindex,follow';
  }, [pathname, search, language]);

  return null;
}
