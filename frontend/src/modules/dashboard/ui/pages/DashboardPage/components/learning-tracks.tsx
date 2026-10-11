import type { DashboardLabels } from '../../../labels';
import type { DashboardOverview } from '../../../../domain';

import { Link } from 'react-router';

import {
  Box,
  Card,
  Chip,
  Stack,
  Button,
  Divider,
  CardHeader,
  Typography,
  LinearProgress,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

/** Adapted from full Minimal src/sections/overview/course/course-continue.tsx. */
export function LearningTracks({
  data,
  labels,
}: {
  data: DashboardOverview;
  labels: DashboardLabels;
}) {
  const tracks = [
    {
      title: labels.namesStats,
      subtitle: data.nextName?.transcription ?? labels.allNames,
      count: data.stats.namesIntroduced,
      total: data.stats.namesTotal,
      arabic: 'الأسماء',
      href: data.nextName ? `/names?name=${data.nextName.id}` : '/names',
      action: labels.openName,
    },
    {
      title: labels.arabic,
      subtitle: data.nextArabicLesson?.title ?? labels.allLessons,
      count: data.stats.arabicLessonsCompleted,
      total: data.stats.arabicLessonsTotal,
      arabic: 'العربية',
      href: data.nextArabicLesson ? `/arabic?lesson=${data.nextArabicLesson.id}` : '/arabic',
      action: labels.openArabic,
    },
  ];
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader title={labels.continue} sx={{ pb: 1 }} />
      <Stack divider={<Divider sx={{ borderStyle: 'dashed' }} />} sx={{ p: 3 }} spacing={3}>
        {tracks.map((track) => (
          <Stack key={track.href} direction={{ xs: 'column', sm: 'row' }} spacing={2.5}>
            <Box
              lang="ar"
              dir="rtl"
              sx={{
                width: { xs: 1, sm: 82 },
                height: 82,
                flexShrink: 0,
                borderRadius: 2,
                bgcolor: 'background.neutral',
                color: 'primary.main',
                fontFamily: 'Amiri,serif',
                fontSize: 25,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {track.arabic}
            </Box>
            <Stack spacing={1.5} sx={{ flexGrow: 1, minWidth: 0 }}>
              <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center">
                <Typography variant="overline" color="text.secondary">
                  {track.title}
                </Typography>
                <Chip label={`${track.count} / ${track.total}`} size="small" variant="soft" />
              </Stack>
              <Typography variant="subtitle1">{track.subtitle}</Typography>
              <LinearProgress
                variant="determinate"
                value={track.total ? (track.count / track.total) * 100 : 0}
                sx={{ height: 5, borderRadius: 1 }}
              />
              <Button
                component={Link}
                to={track.href}
                size="small"
                endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
                sx={{ alignSelf: 'flex-start', px: 0 }}
              >
                {track.action}
              </Button>
            </Stack>
          </Stack>
        ))}
      </Stack>
    </Card>
  );
}
