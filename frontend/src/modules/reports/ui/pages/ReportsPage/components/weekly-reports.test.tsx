import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { LocaleProvider } from 'src/shared/i18n';

import { useReportsLabels } from '../../../labels';
import { reportPeriod, WeeklyReports } from './weekly-reports';

function TestReport({ data }: { data: Record<string, number> }) {
  const labels = useReportsLabels();
  return (
    <WeeklyReports
      labels={labels}
      reports={[{ id: 1, periodStart: '2026-10-05', periodEnd: '2026-10-11', data }]}
    />
  );
}
const render = (data: Record<string, number>) =>
  renderToStaticMarkup(
    <LocaleProvider>
      <ThemeProvider theme={createTheme({ cssVariables: true })}>
        <TestReport data={data} />
      </ThemeProvider>
    </LocaleProvider>
  );
it('groups weekly flows separately from cumulative snapshots', () => {
  const html = render({
    reviews: 17,
    correct: 16,
    accuracy: 94,
    introduced: 0,
    learned_total: 13,
    arabic_reviews: 0,
    arabic_accuracy: 0,
    arabic_items_total: 12,
    arabic_lessons_completed: 0,
    prayer_completed: 2,
    fast_completed: 0,
    favorites_added: 0,
  });
  expect(html).toContain('Allohning ismlari');
  expect(html).toContain('Ibodat va kutubxona');
  expect(html).toContain('Hisobot tuzilgan paytdagi jami');
  expect(html).toContain('94%');
  expect(html).not.toContain('>0%<');
  expect(html).toContain('Bu haftada test topshirilmagan');
});
it('shows missing historical fields as unavailable, not invented zeroes', () => {
  const html = render({ reviews: 1, correct: 1, accuracy: 100 });
  expect(html).toContain('>—<');
  expect(html).not.toContain('>0%<');
});
it('uses real Uzbek month names even when browser ICU has no Uzbek locale data', () => {
  expect(
    reportPeriod({ id: 1, periodStart: '2026-10-05', periodEnd: '2026-10-11', data: {} }, 'uz')
  ).toBe('5–11 oktabr 2026');
  expect(
    reportPeriod({ id: 1, periodStart: '2026-09-28', periodEnd: '2026-10-04', data: {} }, 'uz')
  ).toBe('28 sentabr — 4 oktabr 2026');
});
