import type { Theme } from '@mui/material/styles';

export const coverTones = {
  mint: { surface: '#EFFAF4', ink: '#187957' },
  aqua: { surface: '#EFFAF9', ink: '#147D80' },
  lavender: { surface: '#F6F2FC', ink: '#7950AE' },
  peach: { surface: '#FFF5EF', ink: '#985739' },
  blue: { surface: '#F0F6FC', ink: '#366CA1' },
  rose: { surface: '#FDF1F5', ink: '#A94F71' },
  amber: { surface: '#FFFAED', ink: '#876318' },
} as const;

export type CoverTone = keyof typeof coverTones;

/** Muted category surfaces with contrasting text in both color modes. */
export function learningCover(theme: Theme, tone: CoverTone) {
  const { surface, ink } = coverTones[tone];
  return {
    bgcolor: surface,
    color: ink,
    ...theme.applyStyles('dark', { bgcolor: `${ink}26`, color: surface }),
  };
}
