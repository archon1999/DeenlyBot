import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { LocaleProvider } from 'src/shared/i18n';

import { AudioPlayer } from './index';
import { audioLabels } from './labels';

const tracks = [
  {
    id: '1',
    label: 'Ayah 1',
    voice: 'Reciter',
    url: '/media/1.mp3',
    durationMs: 4000,
    segments: [],
    attribution: 'Audio credit',
    sourceUrl: 'https://example.com',
  },
];
const render = (props: Parameters<typeof AudioPlayer>[0]) =>
  renderToStaticMarkup(
    <LocaleProvider>
      <ThemeProvider theme={createTheme({ cssVariables: true })}>
        <AudioPlayer {...props} />
      </ThemeProvider>
    </LocaleProvider>
  );
it('renders deliberate accessible playback with no autoplay or progress mutation', () => {
  const html = render({ tracks });
  expect(html).toContain('preload="none"');
  expect(html).not.toContain('autoPlay');
  expect(html).not.toContain('autoplay');
  expect(html).toContain(`aria-label="${audioLabels.uz.play}"`);
  expect(html).toContain(`aria-label="${audioLabels.uz.seek}"`);
  expect(html).toContain('Audio credit');
  expect(html).toContain('noopener noreferrer');
  expect(html).not.toContain('O‘rgandim');
  expect(html).toContain('aria-haspopup="menu"');
  expect(html).toContain(`${audioLabels.uz.repeat}: 1×`);
  expect(html).not.toContain('MuiSelect-select');
});
it('renders no dead play buttons when verified audio is unavailable', () => {
  expect(render({ tracks: [] })).not.toContain('<audio');
  expect(render({ tracks: [] })).not.toContain('<button');
  const html = render({ tracks: [], unavailable: true });
  expect(html).toContain(audioLabels.uz.unavailable);
  expect(html).not.toContain('<button');
  expect(html).not.toContain('<audio');
});
it('offers a real playlist and localized controls for all languages', () => {
  const html = render({ tracks: [...tracks, { ...tracks[0], id: '2', label: 'Ayah 2' }] });
  expect(html).toContain(audioLabels.uz.next);
  expect(html).toContain(audioLabels.uz.previous);
  for (const language of ['uz', 'ru', 'en'] as const)
    for (const value of Object.values(audioLabels[language]))
      expect(value.length).toBeGreaterThan(0);
});
