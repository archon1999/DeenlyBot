import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { LocaleProvider } from 'src/shared/i18n';

import { useArabicLabels } from '../../../labels';
import { LessonGrid, categoryTones } from './lesson-grid';

function TestLessons() {
  const labels = useArabicLabels();
  const base = {
    status: 'new' as const,
    summary: 'Short lesson',
    previewArabic: ['ا'],
    estimatedMinutes: 6,
  };
  return (
    <LessonGrid
      labels={labels}
      categories={[
        { key: 'alphabet', title: 'Alifbo va o‘qish' },
        { key: 'prayer_arabic', title: 'Namozni o‘rganish' },
      ]}
      onSelect={() => {}}
      lessons={[
        { ...base, id: 1, order: 1, slug: 'alif', title: 'Alif', category: 'alphabet' },
        { ...base, id: 2, order: 2, slug: 'ba', title: 'Ba', category: 'alphabet' },
        { ...base, id: 3, order: 1, slug: 'takbir', title: 'Takbir', category: 'prayer_arabic' },
      ]}
    />
  );
}
it('assigns one fixed tone per category rather than changing with lesson order', () => {
  expect(categoryTones.alphabet).toBe('mint');
  expect(new Set(Object.values(categoryTones)).size).toBe(7);
  const html = renderToStaticMarkup(
    <LocaleProvider>
      <ThemeProvider theme={createTheme({ cssVariables: true })}>
        <TestLessons />
      </ThemeProvider>
    </LocaleProvider>
  );
  expect(html).toContain('#EFFAF4');
  expect(html).toContain('#FFF5EF');
  expect(html).toContain('Namozni o‘rganish');
  expect(html).toContain('Alifbo va o‘qish');
});
