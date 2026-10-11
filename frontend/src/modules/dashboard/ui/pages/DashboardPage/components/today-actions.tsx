import type { DashboardLabels } from '../../../labels';
import type { DashboardOverview } from '../../../../domain';

import { Link } from 'react-router';

import { Box, Card, Chip, Stack, Button, Divider, CardHeader, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

/** List composition adapted from full Minimal course/course-reminders.tsx. */
export function TodayActions({
  data,
  labels,
}: {
  data: DashboardOverview;
  labels: DashboardLabels;
}) {
  const current = data.qada.current;
  return (
    <Stack spacing={3}>
      <Card>
        <CardHeader title={labels.review} subheader={labels.reviewHint} />
        <Stack spacing={2} divider={<Divider sx={{ borderStyle: 'dashed' }} />} sx={{ p: 3 }}>
          {[
            { label: labels.nameReviews, count: data.reviewsDue, href: '/names' },
            { label: labels.arabicReviews, count: data.arabicReviewsDue, href: '/arabic' },
          ].map((row) => (
            <Stack
              key={row.href}
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              spacing={1}
            >
              <Stack direction="row" spacing={1.5} alignItems="center">
                <Box
                  sx={{
                    display: 'flex',
                    p: 1,
                    borderRadius: 1.5,
                    color: 'primary.main',
                    bgcolor: 'background.neutral',
                  }}
                >
                  <Iconify icon="solar:restart-bold" width={20} />
                </Box>
                <Box>
                  <Typography variant="subtitle2">{row.label}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {row.count} · {labels.review}
                  </Typography>
                </Box>
              </Stack>
              <Button component={Link} to={row.href} size="small">
                {labels.review}
              </Button>
            </Stack>
          ))}
        </Stack>
      </Card>
      <Card sx={{ p: 3, bgcolor: 'background.paper' }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2}>
          <Stack spacing={1}>
            <Typography variant="overline" color="text.secondary">
              {labels.qada}
            </Typography>
            <Typography variant="h5">
              {current ? labels[current.prayerType] : labels.qadaEmpty}
            </Typography>
            {current && (
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="caption" color="text.secondary">
                  {current.prayerDate}
                </Typography>
                <Chip label={labels[current.source]} size="small" variant="soft" />
              </Stack>
            )}
            <Button
              component={Link}
              to="/qada"
              size="small"
              endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
              sx={{ alignSelf: 'flex-start', px: 0 }}
            >
              {labels.qadaLink}
            </Button>
          </Stack>
          <Iconify
            icon="solar:calendar-date-bold"
            width={48}
            aria-hidden
            sx={{ color: 'primary.main', opacity: 0.65 }}
          />
        </Stack>
      </Card>
    </Stack>
  );
}
