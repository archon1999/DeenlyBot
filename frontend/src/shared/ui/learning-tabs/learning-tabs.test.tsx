import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { LearningTabs } from './index';

it('renders server-provided categories in order with mobile scroll and 8% mint active', () => {
  const categories = [
    'Alifbo',
    'Qur’on so‘zlari',
    'Nahv',
    'Namoz arabchasi',
    'Sarf',
    'Kundalik iboralar',
    'Tinglab tushunish',
  ].map((title, index) => ({ key: String(index), title }));
  const html = renderToStaticMarkup(
    <ThemeProvider theme={createTheme({ cssVariables: true })}>
      <LearningTabs value="3" items={categories} onChange={() => {}} label="Darslar" />
    </ThemeProvider>
  );
  expect(html.match(/role="tab"/g)).toHaveLength(7);
  expect(html).toContain('MuiTabs-scrollableX');
  expect(html).toContain('/ 8%)');
  for (const category of categories) expect(html).toContain(category.title);
});
