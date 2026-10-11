import type { WorshipLabels } from '../../../labels';
import type { CurrentQada } from '../../../../domain';

import { Box, Card, Chip, Alert, Stack, Button, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

export function CurrentQadaCard({
  current,
  onComplete,
  busy,
  error,
  labels,
  onConfigure,
}: {
  current: CurrentQada | null;
  onComplete: () => void;
  busy: boolean;
  error: Error | null;
  labels: WorshipLabels;
  onConfigure?: () => void;
}) {
  return (
    <Card
      sx={{
        p: { xs: 3, md: 4 },
        position: 'relative',
        overflow: 'hidden',
        bgcolor: 'primary.dark',
        color: 'common.white',
      }}
    >
      <Iconify
        aria-hidden
        icon="solar:cloudy-moon-bold-duotone"
        sx={{ width: 230, height: 230, right: -65, top: -25, position: 'absolute', opacity: 0.1 }}
      />
      <Stack spacing={2.5} sx={{ position: 'relative', zIndex: 1, height: 1 }}>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Box sx={{ display: 'flex', p: 1.25, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 2 }}>
            <Iconify icon="solar:clock-circle-bold" width={24} />
          </Box>
          <Typography variant="h6">{labels.current}</Typography>
        </Stack>
        {current ? (
          <>
            <Chip
              label={labels[current.source]}
              size="small"
              sx={{
                alignSelf: 'flex-start',
                bgcolor: 'rgba(255,255,255,0.13)',
                color: 'common.white',
              }}
            />
            <Typography variant="h3">{labels[current.prayerType]}</Typography>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ opacity: 0.8 }}>
              <Iconify icon="solar:calendar-date-bold" width={18} />
              <Typography variant="body2">{current.prayerDate}</Typography>
            </Stack>
            <Button
              variant="contained"
              size="large"
              loading={busy}
              onClick={onComplete}
              startIcon={<Iconify icon="eva:checkmark-fill" />}
              sx={{
                alignSelf: 'flex-start',
                bgcolor: 'common.white',
                color: 'primary.dark',
                '&:hover': { bgcolor: 'grey.200' },
              }}
            >
              {labels.complete}
            </Button>
          </>
        ) : (
          <Typography sx={{ opacity: 0.8, py: 2 }}>{labels.empty}</Typography>
        )}
        {onConfigure && (
          <Button
            color="inherit"
            variant="outlined"
            onClick={onConfigure}
            startIcon={<Iconify icon="solar:settings-bold" />}
            sx={{ alignSelf: 'flex-start', borderColor: 'rgba(255,255,255,0.35)' }}
          >
            {labels.configure}
          </Button>
        )}
        {error && <Alert severity="error">{error.message}</Alert>}
      </Stack>
    </Card>
  );
}
