import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { LocaleProvider } from 'src/shared/i18n';

import { LocalizedTimePicker } from './index';

it('renders an accessible MUI time field instead of a native browser time input', () => {
  const html = renderToStaticMarkup(
    <LocaleProvider>
      <ThemeProvider theme={createTheme({ cssVariables: true })}>
        <LocalizedTimePicker
          label="Hisobot vaqti"
          value="20:00:00"
          onChange={() => {}}
          onValidityChange={() => {}}
        />
      </ThemeProvider>
    </LocaleProvider>
  );
  expect(html).toContain('Hisobot vaqti');
  expect(html).toContain('MuiPickers');
  expect(html).toContain('Vaqtni tanlash');
  expect(html).not.toContain('type="time"');
  expect(html).toContain('role="spinbutton"');
});
