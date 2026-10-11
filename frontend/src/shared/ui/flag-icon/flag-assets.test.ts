import { it, expect } from 'vitest';
import { readFileSync } from 'node:fs';

it('keeps the Union Jack red diagonals clipped within their white borders', () => {
  const svg = readFileSync(
    new URL('../../../../public/assets/icons/flags/gb.svg', import.meta.url),
    'utf8'
  );
  expect(svg).toContain('viewBox="0 0 60 30"');
  expect(svg).toContain('<clipPath id="diagonals">');
  expect(svg).toContain('stroke="#fff" stroke-width="6"');
  expect(svg).toContain('stroke="#c8102e" stroke-width="4" clip-path="url(#diagonals)"');
  expect(svg).not.toContain('fill="#c8102e"');
  expect(svg).not.toMatch(/<image|<script/);
});
