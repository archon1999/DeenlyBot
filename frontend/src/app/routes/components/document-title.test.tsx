import { MemoryRouter } from 'react-router';
import { it, expect, describe } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { LocaleProvider } from 'src/shared/i18n';
import { failureLabels } from 'src/shared/ui/failure-page';

import { getPageTitle, DocumentTitle } from './document-title';

const titles = {
  '/': ['Bugun', 'Сегодня', 'Today'],
  '/names': ['Allohning ismlari', 'Имена Аллаха', 'Names of Allah'],
  '/arabic': ['Arab tili', 'Арабский язык', 'Arabic'],
  '/library': ['Kutubxona', 'Библиотека', 'Library'],
  '/qada': ['Qazo', 'Када', 'Qada'],
  '/worship': ['Qazo', 'Када', 'Qada'],
  '/calendar': ['Taqvim', 'Календарь', 'Calendar'],
  '/reports': ['Hisobotlar', 'Отчёты', 'Reports'],
  '/settings': ['Sozlamalar', 'Настройки', 'Settings'],
  '/profile': ['Mening profilim', 'Мой профиль', 'My profile'],
  '/login': ['Kirish', 'Войти', 'Sign in'],
} as const;

describe('localized browser page titles', () => {
  it.each(['uz', 'ru', 'en'] as const)('covers every existing page in %s', (language) => {
    const localeIndex = ['uz', 'ru', 'en'].indexOf(language);
    for (const [path, labels] of Object.entries(titles)) {
      expect(getPageTitle(path, '', language)).toBe(`${labels[localeIndex]} | Deenly.uz`);
    }
  });

  it.each([
    ['uz', 'Akkaunt yaratish'],
    ['ru', 'Создать аккаунт'],
    ['en', 'Create account'],
  ] as const)('distinguishes account creation from sign-in in %s', (language, label) => {
    expect(getPageTitle('/login', '?next=%2Flibrary&mode=register', language)).toBe(
      `${label} | Deenly.uz`
    );
  });

  it.each(['uz', 'ru', 'en'] as const)('uses the actual 404 fallback wording in %s', (language) => {
    for (const path of ['/missing', '/library/missing', '/namesake', '/error']) {
      expect(getPageTitle(path, '?mode=register', language)).toBe(
        `${failureLabels[language].notFound} | Deenly.uz`
      );
    }
  });

  it('matches case-insensitive routes and trailing slashes without treating unknown prefixes as pages', () => {
    expect(getPageTitle('/NAMES/', '', 'uz')).toBe('Allohning ismlari | Deenly.uz');
    expect(getPageTitle('/login/', '?mode=register', 'en')).toBe('Create account | Deenly.uz');
    expect(getPageTitle('/', '?mode=register', 'en')).toBe('Today | Deenly.uz');
  });

  it('ignores unrelated query parameters and accepts only the registration mode used by the page', () => {
    for (const search of ['', '?mode=login', '?mode=unknown', '?next=%2Flogin%3Fmode%3Dregister']) {
      expect(getPageTitle('/login', search, 'en')).toBe('Sign in | Deenly.uz');
    }
    expect(getPageTitle('/library', '?mode=register', 'en')).toBe('Library | Deenly.uz');
  });

  it('renders no visible layout or application chrome', () => {
    expect(
      renderToStaticMarkup(
        <MemoryRouter initialEntries={['/library']}>
          <LocaleProvider>
            <DocumentTitle />
          </LocaleProvider>
        </MemoryRouter>
      )
    ).toBe('');
  });
});
