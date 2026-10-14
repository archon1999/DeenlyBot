import type { ReactNode } from 'react';

import { Box, Button } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { Iconify } from 'src/shared/ui/iconify';

const labels = {
  uz: 'Takrorlashga o‘tish',
  ru: 'Перейти к повторению',
  en: 'Go to review',
};

export function ReviewLink({ targetId }: { targetId: string }) {
  const { language } = useLocale();
  return (
    <Button
      component="a"
      href={`#${targetId}`}
      aria-controls={targetId}
      endIcon={<Iconify icon="solar:arrow-right-linear" width={20} />}
      sx={{ flexShrink: 0, whiteSpace: 'nowrap', minHeight: 44 }}
      onClick={(event) => {
        const target = document.getElementById(targetId);
        if (!target) return;
        event.preventDefault();
        target.focus({ preventScroll: true });
        target.scrollIntoView({
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
            ? 'auto'
            : 'smooth',
          block: 'start',
        });
      }}
    >
      {labels[language]}
    </Button>
  );
}

export function ReviewSection({ id, children }: { id: string; children: ReactNode }) {
  return (
    <Box
      id={id}
      tabIndex={-1}
      sx={{
        scrollMarginTop: 24,
        '&:focus-visible': {
          outline: '2px solid',
          outlineColor: 'primary.main',
          outlineOffset: 4,
          borderRadius: 3,
        },
      }}
    >
      {children}
    </Box>
  );
}
