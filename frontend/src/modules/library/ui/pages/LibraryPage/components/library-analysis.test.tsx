import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { ThemeProvider } from '@mui/material/styles';

import { LocaleProvider } from 'src/shared/i18n';
import { createTheme } from 'src/app/theme/create-theme';

import { useLibraryLabels } from '../../../labels';
import { LibraryAnalysisView } from './library-analysis';

function Analysis() {
  const labels = useLibraryLabels();
  return (
    <LibraryAnalysisView
      labels={labels}
      analysis={{
        summary: 'Summary',
        context: 'Context',
        explanation: 'Language note',
        verses: [
          {
            key: '112:1',
            arabicText: 'قُلْ',
            translation: 'Say',
            transcription: 'Qul',
            words: [
              {
                id: '1',
                arabicText: 'قُلْ',
                root: 'ق و ل',
                meaning: 'Say',
                transcription: 'Qul',
                grammarNote: 'Imperative',
              },
            ],
          },
        ],
      }}
    />
  );
}
it('renders structured verse analysis and keyboard-operable RTL word buttons', () => {
  const html = renderToStaticMarkup(
    <LocaleProvider>
      <ThemeProvider theme={createTheme()}>
        <Analysis />
      </ThemeProvider>
    </LocaleProvider>
  );
  expect(html).toContain('Summary');
  expect(html).toContain('Language note');
  expect(html).toContain('112:1');
  expect(html).toContain('lang="ar" dir="rtl"');
  expect(html).toContain('aria-pressed="false"');
});
