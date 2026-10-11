import { it, vi, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { EstimatedDateIndicator } from './estimated-date-indicator';

const locale = vi.hoisted(() => ({ language: 'uz' as 'uz' | 'ru' | 'en' }));
vi.mock('src/shared/i18n', () => ({ useLocale: () => locale }));

it.each([
  ['uz', 'Taxminiy sana', 'mahalliy e’longa'],
  ['ru', 'Предварительная дата', 'местных объявлений'],
  ['en', 'Estimated date', 'local announcements'],
] as const)(
  'provides a localized, keyboard-accessible information tooltip in %s',
  (language, label, hint) => {
    locale.language = language;
    const html = renderToStaticMarkup(<EstimatedDateIndicator isEstimated />);
    expect(html).toContain(`aria-label="${label}"`);
    expect(html).toContain(hint);
    expect(html).toContain('<button');
    expect(html).toContain('tabindex="0"');
    expect(html).toContain('iconify--eva');
    expect(html).not.toContain('MuiChip');
  }
);

it('does not show an estimated indicator for confirmed dates', () => {
  expect(renderToStaticMarkup(<EstimatedDateIndicator isEstimated={false} />)).toBe('');
});
