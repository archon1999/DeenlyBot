import type { Theme, CSSObject } from '@mui/material/styles';

import { it, expect } from 'vitest';

import { card } from './card';
import { customShadows } from '../custom-shadows';

it('uses a borderless card surface and the shared soft-shadow token', () => {
  const theme = {
    vars: { customShadows: { card: 'soft-card-shadow' } },
    shape: { borderRadius: 8 },
  } as unknown as Theme;
  const root = card.MuiCard!.styleOverrides!.root as (props: { theme: Theme }) => CSSObject;
  expect(root({ theme })).toMatchObject({
    border: 0,
    boxShadow: 'var(--card-shadow, soft-card-shadow)',
  });
});

it.each(['light', 'dark'] as const)(
  'keeps the %s card shadow diffuse without a border-like halo',
  (mode) => {
    const shadow = customShadows[mode]?.card;
    expect(shadow).toBeDefined();
    expect(shadow).toContain('0 4px 12px -2px');
    expect(shadow).toContain('0 12px 28px -4px');
    expect(shadow).not.toContain('0 0 2px');
  }
);
