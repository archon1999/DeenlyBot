import { it, expect } from 'vitest';
import { readFileSync } from 'node:fs';

import { ARCH_D_PATH } from './arch-d-path';

it('uses the selected Arch D geometry consistently in the UI and static brand assets', () => {
  for (const file of ['logo/arch-d.svg', 'favicon.svg']) {
    const svg = readFileSync(new URL(`../../../../public/${file}`, import.meta.url), 'utf8');
    expect(svg).toContain(`d="${ARCH_D_PATH}"`);
    expect(svg).toContain('fill-rule="evenodd"');
    expect(svg).not.toMatch(/<image|<script|https?:\/\/(?!www\.w3\.org)/);
  }
});
