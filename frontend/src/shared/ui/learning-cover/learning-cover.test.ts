import { it, expect } from 'vitest';

import { coverTones } from './index';

function luminance(hex: string) {
  const channels = hex
    .slice(1)
    .match(/../g)!
    .map((value) => parseInt(value, 16) / 255)
    .map((value) => (value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4));
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}
it.each(Object.entries(coverTones))(
  'keeps readable text contrast on the light %s category surface',
  (_, tone) => {
    expect((luminance(tone.surface) + 0.05) / (luminance(tone.ink) + 0.05)).toBeGreaterThanOrEqual(
      4.5
    );
  }
);
