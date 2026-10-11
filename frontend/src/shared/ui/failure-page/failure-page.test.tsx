import { it, vi, expect, afterEach } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { ErrorBoundary, AppErrorBoundary } from 'src/app/routes/components/error-boundary';

import {
  FailurePage,
  failureLabels,
  readFailureMode,
  applyFailureMode,
  resolveFailureLanguage,
} from './index';

it.each(['uz', 'ru', 'en'] as const)(
  'renders localized404 and error without any application providers in %s',
  (language) => {
    for (const kind of ['404', 'error'] as const) {
      const html = renderToStaticMarkup(<FailurePage kind={kind} language={language} />);
      const labels = failureLabels[language];
      expect(html).toContain(kind === '404' ? labels.notFound : labels.error);
      expect(html).toContain(labels.home);
      expect(html).toContain(labels.retry);
      expect(html).toContain('href="/"');
      expect(html).toContain('tabindex="-1"');
      expect(html).toContain('aria-hidden="true"');
      expect(html).toContain('data-color-scheme="dark"');
      expect(html).not.toContain('Qur’an');
      expect(html.match(/<main\b/g)).toHaveLength(1);
      expect(html).not.toMatch(/<(header|nav|aside)\b/);
    }
  }
);
it('uses a safe language fallback and never concatenates three translations', () => {
  expect(resolveFailureLanguage('ru-RU')).toBe('ru');
  expect(resolveFailureLanguage('en-GB')).toBe('en');
  expect(resolveFailureLanguage('ar')).toBe('uz');
  const html = renderToStaticMarkup(<ErrorBoundary />);
  expect(html).toContain(failureLabels.uz.error);
  expect(html).not.toContain(failureLabels.ru.error);
});
it('has an actual root boundary outside RouterProvider', () => {
  expect(AppErrorBoundary.getDerivedStateFromError()).toEqual({ failed: true });
  const boundary = new AppErrorBoundary({ children: 'App' });
  boundary.state = { failed: true };
  expect(boundary.render()).toEqual(<ErrorBoundary />);
});
afterEach(() => vi.unstubAllGlobals());
it('offers independent language and light/darkcontrols with bounded viewport layout', () => {
  const html = renderToStaticMarkup(<FailurePage kind="error" language="en" />);
  expect(html).toContain('aria-label="Light appearance"');
  expect(html).toContain('aria-label="Dark appearance"');
  expect(html).toContain('aria-label="O‘zbekcha"');
  expect(html).toContain('aria-label="Русский"');
  expect(html).toContain('aria-label="English"');
  expect(html).toContain('height: 100dvh');
  expect(html).toContain('overflow: auto');
  expect(html).toContain('max-height:650px');
});
it.each(['404', 'error'] as const)(
  'uses the entire viewport without dashboard chrome for %s',
  (kind) => {
    const html = renderToStaticMarkup(<FailurePage kind={kind} />);
    expect(html).toContain('height: 100dvh;');
    expect(html).not.toContain('layout-header-');
    expect(html).not.toMatch(/<(header|nav|aside)\b/);
    expect(html).toContain('deenly-failure__controls');
  }
);
it('shares only the existing non-private theme-modepreference with the independent fallback', () => {
  const storage = { getItem: vi.fn().mockReturnValue('dark'), setItem: vi.fn() };
  const root = {
    getAttribute: vi.fn().mockReturnValue(null),
    setAttribute: vi.fn(),
    style: { colorScheme: '' },
  };
  vi.stubGlobal('window', { localStorage: storage });
  vi.stubGlobal('document', { documentElement: root });
  expect(readFailureMode()).toBe('dark');
  applyFailureMode('light');
  expect(storage.setItem).toHaveBeenCalledWith('theme-mode', 'light');
  expect(root.setAttribute).toHaveBeenCalledWith('data-color-scheme', 'light');
  expect(root.style.colorScheme).toBe('light');
  expect(storage.setItem).toHaveBeenCalledTimes(1);
});
