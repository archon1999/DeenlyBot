import { MemoryRouter } from 'react-router';
import { it, vi, expect, afterEach } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ThemeProvider } from '@mui/material/styles';

import { LocaleProvider } from 'src/shared/i18n';
import { createTheme } from 'src/app/theme/create-theme';

import { LoginPage } from './LoginPage';

vi.mock('../../../application', async (original) => ({
  ...(await original<object>()),
  useSession: () => ({
    authenticated: false,
    profile: null,
    isLoading: false,
    error: null,
    refreshSession: vi.fn(),
  }),
}));
afterEach(() => vi.unstubAllGlobals());
const render = (path: string) => {
  vi.stubGlobal('window', { location: { origin: 'http://localhost' } });
  return renderToStaticMarkup(
    <QueryClientProvider client={new QueryClient()}>
      <LocaleProvider>
        <ThemeProvider theme={createTheme()}>
          <MemoryRouter initialEntries={[path]}>
            <LoginPage />
          </MemoryRouter>
        </ThemeProvider>
      </LocaleProvider>
    </QueryClientProvider>
  );
};
it('keeps explicitlogin available with credentials, Telegram and deliberate guest entry', () => {
  const html = render('/login');
  expect(html.toLowerCase()).toContain('autocomplete="email"');
  expect(html.toLowerCase()).toContain('autocomplete="current-password"');
  expect(html).toContain('Telegram orqali kirish');
  expect(html).toContain('Mehmon sifatida boshlash');
});
it('keeps registration and its password requirements on the same split layout', () => {
  const html = render('/login?mode=register');
  expect(html.toLowerCase()).toContain('autocomplete="given-name"');
  expect(html.toLowerCase()).toContain('autocomplete="new-password"');
  expect(html.toLowerCase()).toContain('minlength="8"');
});
it('bounds document height while keeping validation and confirmation overflow reachable', () => {
  const html = render('/login');
  expect(html).toContain('height:100dvh');
  expect(html).toContain('overflow-y:auto');
  expect(html).toContain('minmax(0,1fr) minmax(0,1fr)');
  expect(html).toContain('Ilm, ibodat va xotirjamlik');
  expect(html).toContain('aria-hidden="true"');
});
it('uses medium credential fields, top-righttheme and language controls, and removes the guest slogan', () => {
  const html = render('/login?mode=register');
  expect(html).not.toContain('MuiInputBase-sizeSmall');
  expect(html).toContain('aria-label="Yorug‘/qorong‘i ko‘rinish"');
  expect(html).toContain('aria-label="Tilni tanlash"');
  expect(html).not.toContain('Mehmon sifatida boshlang. Akkauntni xohlagan paytingizda yarating.');
  expect(html).toContain('overflow-y:auto');
  expect(html).toContain('height:100dvh');
});
it('anchors the mobile form below the header and limits decorative art to tall viewports', () => {
  const html = render('/login?mode=register');
  expect(html).toContain('data-testid="auth-form-block"');
  expect(html).toContain('data-testid="auth-mobile-art"');
  expect(html).toContain('max-height:799px');
  expect(html).toContain('max-height:700px');
  expect(html).toContain('margin-top:var(--spacing)');
  expect(html).toContain('margin-bottom:0');
  expect(html).toContain('max-height:96px');
  expect(html).toContain('margin-bottom:calc(2.5 * var(--spacing))');
  expect(html).toContain('gap:calc(2 * var(--spacing))');
  expect(html).toContain('Deenlyga xush kelibsiz');
});
