import type { DashboardLabels } from '../../../labels';

import { Box, Stack, Typography } from '@mui/material';

export function DashboardHeading({
  labels,
}: {
  labels: Pick<DashboardLabels, 'title' | 'subtitle'>;
}) {
  return (
    <Stack
      component="header"
      direction={{ xs: 'column', sm: 'row' }}
      alignItems={{ xs: 'stretch', sm: 'center' }}
      justifyContent="space-between"
      spacing={{ xs: 1.5, sm: 3 }}
      useFlexGap
    >
      <Box sx={{ minWidth: 0 }}>
        <Typography variant="h3" component="h1">{labels.title}</Typography>
        <Typography color="text.secondary" sx={{ mt: 1 }}>
          {labels.subtitle}
        </Typography>
      </Box>
      <Typography
        component="p"
        lang="ar"
        dir="rtl"
        sx={(theme) => ({
          fontFamily: 'Amiri, "Traditional Arabic", serif',
          fontSize: { xs: 28, sm: 32, md: 38 },
          fontWeight: 400,
          lineHeight: 2,
          letterSpacing: 0,
          color: 'primary.dark',
          textAlign: { xs: 'center', sm: 'right' },
          order: { xs: -1, sm: 0 },
          flexShrink: 0,
          maxWidth: '100%',
          ...theme.applyStyles('dark', { color: 'primary.light' }),
        })}
      >
        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
      </Typography>
    </Stack>
  );
}
