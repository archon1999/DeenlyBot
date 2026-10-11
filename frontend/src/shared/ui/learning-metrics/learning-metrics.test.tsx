import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { LearningMetrics } from './index';

it('shares one responsive three-card overview and a single progress bar', () => {
  const html = renderToStaticMarkup(
    <ThemeProvider theme={createTheme({ cssVariables: true })}>
      <LearningMetrics
        items={[
          { label: 'Studied', value: '4 / 11', progress: 36, color: 'success' },
          { label: 'Accuracy', value: '50%', color: 'primary' },
          { label: 'Reviews due', value: 2, color: 'warning' },
        ]}
      />
    </ThemeProvider>
  );
  expect(html.match(/<div[^>]*class="[^"]*\bMuiCard-root\b[^"]*"/g)).toHaveLength(3);
  expect(html.match(/role="progressbar"/g)).toHaveLength(1);
  expect(html).toContain('4 / 11');
  expect(html).toContain('50%');
  expect(html).toContain('grid-template-columns:1fr');
  expect(html).toContain('grid-template-columns:repeat(3,1fr)');
});
