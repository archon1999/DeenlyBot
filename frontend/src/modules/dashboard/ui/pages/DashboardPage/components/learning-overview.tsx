import type { DashboardLabels } from '../../../labels';
import type { DashboardOverview } from '../../../../domain';

import { Link } from 'react-router';

import { Box, Chip, Stack, Button, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

/** Adapted from full Minimal src/sections/overview/app/app-welcome.tsx. */
export function LearningOverview({
  data,
  labels,
  firstName,
}: {
  data: DashboardOverview;
  labels: DashboardLabels;
  firstName?: string;
}) {
  const next = data.nextName;
  return (
    <Box
      sx={(theme) => ({
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 3,
        boxShadow: theme.vars.customShadows.card,
        color: 'common.white',
        p: { xs: 3, md: 5 },
        minHeight: { md: 300 },
        background: `linear-gradient(120deg,${theme.vars.palette.primary.darker} 0%,${theme.vars.palette.primary.dark} 68%,${theme.vars.palette.primary.main} 140%)`,
      })}
    >
      <Box
        aria-hidden
        sx={{
          position: 'absolute',
          right: -80,
          top: -110,
          width: 420,
          height: 420,
          border: 1,
          borderColor: 'rgba(255,255,255,.1)',
          borderRadius: '50%',
        }}
      />
      <Box
        aria-hidden
        sx={{
          position: 'absolute',
          right: -30,
          top: -60,
          width: 320,
          height: 320,
          border: 1,
          borderColor: 'rgba(255,255,255,.1)',
          borderRadius: '50%',
        }}
      />
      <Stack
        direction={{ xs: 'column', md: 'row' }}
        spacing={{ xs: 2, md: 6 }}
        alignItems={{ md: 'center' }}
        sx={{ position: 'relative' }}
      >
        <Stack spacing={2.5} sx={{ flexGrow: 1, minWidth: 0, alignItems: 'flex-start' }}>
          <Typography variant="body2" sx={{ opacity: 0.7 }}>
            {labels.greeting}
            {firstName ? `, ${firstName}` : ''}.
          </Typography>
          <Chip
            label={next ? `${labels.name} · ${next.order}` : labels.continue}
            size="small"
            sx={{ bgcolor: 'rgba(255,255,255,.12)', color: 'inherit' }}
          />
          <Box>
            <Typography variant="h3" component="h2" sx={{ lineHeight: 1.3 }}>
              {next ? next.transcription : labels.allNames}
            </Typography>
            <Typography sx={{ mt: 1.5, maxWidth: 500, opacity: 0.78, lineHeight: 1.8 }}>
              {next ? next.meaning : labels.allNamesHint}
            </Typography>
          </Box>
          <Button
            component={Link}
            to={next ? `/names?name=${next.id}` : '/names'}
            variant="contained"
            color="inherit"
            endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={18} />}
            sx={{
              bgcolor: 'common.white',
              color: 'primary.darker',
              px: 3,
              minHeight: 46,
              '&:hover': { bgcolor: 'grey.200' },
            }}
          >
            {next ? labels.openName : labels.review}
          </Button>
        </Stack>
        {next && (
          <Box
            sx={{
              position: 'relative',
              width: { xs: '100%', md: 320 },
              flexShrink: 0,
              textAlign: 'center',
              py: { xs: 1, md: 3 },
            }}
          >
            <Box
              aria-hidden
              sx={{
                position: 'absolute',
                inset: 0,
                opacity: 0.08,
                background: 'url(/assets/background/shape-circle-3.svg) center/contain no-repeat',
              }}
            />
            <Typography
              lang="ar"
              dir="rtl"
              sx={{
                position: 'relative',
                fontFamily: 'Amiri, "Traditional Arabic", serif',
                fontSize: { xs: 56, md: 82 },
                lineHeight: 1.9,
                textShadow: '0 8px 32px rgba(0,0,0,.1)',
              }}
            >
              {next.arabic}
            </Typography>
          </Box>
        )}
      </Stack>
    </Box>
  );
}
