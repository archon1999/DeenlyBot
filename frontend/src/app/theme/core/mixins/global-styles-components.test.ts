import type { Theme } from '@mui/material/styles';

import { it, expect, describe } from 'vitest';

import { paperStyles } from './global-styles-components';

const theme = {
  spacing: (value: number) => `${value * 8}px`,
  shape: { borderRadius: 8 },
  vars: {
    palette: { background: { paperChannel: '255 255 255' } },
    customShadows: { dropdown: 'dropdown-shadow' },
  },
} as unknown as Theme;

describe('flat overlay paper styles', () => {
  it('keeps drawers gradient-free while retaining backdrop blur', () => {
    const styles = paperStyles(theme);
    expect(styles.backgroundImage).toBe('none');
    expect(styles.backdropFilter).toBe('blur(20px)');
  });

  it('keeps dropdowns flat and preserves their shape, shadow and custom background', () => {
    const styles = paperStyles(theme, { dropdown: true, color: '#123456', blur: 12 });
    expect(styles).toMatchObject({
      backgroundImage: 'none',
      backgroundColor: '#123456',
      backdropFilter: 'blur(12px)',
      padding: '4px',
      borderRadius: '10px',
      boxShadow: 'dropdown-shadow',
    });
  });
});
