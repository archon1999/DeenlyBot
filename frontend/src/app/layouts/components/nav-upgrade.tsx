import type { BoxProps } from '@mui/material/Box';

import { Box, Typography } from '@mui/material';

import { useLocale } from 'src/shared/i18n';

export function NavUpgrade(props: BoxProps) {
  const { language } = useLocale();
  const text = {
    uz: 'Oz bo‘lsa ham, davomli.',
    ru: 'Понемногу, но постоянно.',
    en: 'A little, consistently.',
  }[language];
  return (
    <Box {...props} sx={{ px: 3, py: 4 }}>
      <Typography variant="caption" color="text.secondary">
        {text}
      </Typography>
      <Typography variant="subtitle2" color="primary.main" sx={{ mt: 0.5 }}>
        Deenly.uz
      </Typography>
    </Box>
  );
}
