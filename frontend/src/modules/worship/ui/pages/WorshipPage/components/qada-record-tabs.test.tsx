import type { QadaRecord } from '../../../../domain';

import { it, vi, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { ThemeProvider } from '@mui/material/styles';

import { createTheme } from 'src/app/theme/create-theme';

import { useWorshipLabels } from '../../../labels';
import { QadaRecordTabs } from './qada-record-tabs';

const locale = vi.hoisted(() => ({ language: 'uz' as 'uz' | 'ru' | 'en' }));
vi.mock('src/shared/i18n', () => ({ useLocale: () => locale }));
const rows: QadaRecord[] = Array.from({ length: 26 }, (_, index) => ({
  id: index + 1,
  source: 'manual',
  prayerDate: `2026-09-${String(index + 1).padStart(2, '0')}`,
  prayerType: 'isha',
  status: 'pending',
  completedAt: null,
}));
function Fixture({ empty = false }: { empty?: boolean }) {
  const labels = useWorshipLabels();
  return (
    <ThemeProvider theme={createTheme()}>
      <QadaRecordTabs manualQueue={empty ? [] : rows} history={[]} labels={labels} />
    </ThemeProvider>
  );
}

it.each([
  ['uz', 'Qazo navbati va tarixi'],
  ['ru', 'Очередь и история када'],
  ['en', 'Qada queue and history'],
] as const)(
  'keeps %s tabs outside a bounded keyboard-accessible scroll panel',
  (language, name) => {
    locale.language = language;
    const html = renderToStaticMarkup(<Fixture />);
    expect(html).toContain(`aria-label="${name}"`);
    expect(html).toContain('role="tabpanel"');
    expect(html).toContain('aria-labelledby=');
    expect(html).toContain('tabindex="0"');
    expect(html).toContain('max-height:360px');
    expect(html).toContain('max-height:480px');
    expect(html).toContain('overscroll-behavior:contain');
    expect(html).toContain('2026-09-01');
    expect(html).toContain('2026-09-26');
    expect(html).toContain('background-color:rgba(var(--palette-primary-mainChannel) / 8%)');
  }
);

it('keeps empty queues readable without inventing rows', () => {
  locale.language = 'uz';
  const html = renderToStaticMarkup(<Fixture empty />);
  expect(html).toContain('Qo‘lda qo‘shilgan navbat bo‘sh.');
  expect(html).not.toContain('2026-09-01');
});
