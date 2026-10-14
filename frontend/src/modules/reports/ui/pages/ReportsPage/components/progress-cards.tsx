import type { ReportsLabels } from '../../../labels';
import type { WeeklyReport, ProgressStats } from '../../../../domain';

import {
  Box,
  Card,
  Stack,
  Typography,
  CardHeader,
  LinearProgress,
  CircularProgress,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { MetricCard } from 'src/shared/ui/metric-card';

import { reportCount } from '../../../../domain';

export function ProgressCards({
  stats,
  labels,
  latestReport,
}: {
  stats: ProgressStats;
  labels: ReportsLabels;
  latestReport?: WeeklyReport;
}) {
  const nameProgress = stats.namesTotal ? (stats.namesIntroduced / stats.namesTotal) * 100 : 0;
  const lessonProgress = stats.arabicLessonsTotal
    ? (stats.arabicLessonsCompleted / stats.arabicLessonsTotal) * 100
    : 0;
  const learnedProgress = stats.namesIntroduced
    ? (stats.namesLearned / stats.namesIntroduced) * 100
    : 0;
  return (
    <Stack spacing={3}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2,1fr)', lg: 'repeat(4,1fr)' },
          gap: 3,
        }}
      >
        <MetricCard
          label={labels.names}
          value={`${stats.namesIntroduced} / ${stats.namesTotal}`}
          icon={<Iconify icon="solar:notebook-bold-duotone" width={28} />}
          progress={nameProgress}
          helper={`${Math.round(nameProgress)}% ${labels.coverage}`}
          details={[
            { label: labels.retained, value: stats.namesLearned },
            {
              label: labels.remaining,
              value: Math.max(0, stats.namesTotal - stats.namesIntroduced),
            },
          ]}
        />
        <MetricCard
          label={labels.arabic}
          value={`${stats.arabicLessonsCompleted} / ${stats.arabicLessonsTotal}`}
          icon={<Iconify icon="solar:notes-bold-duotone" width={28} />}
          color="info"
          progress={lessonProgress}
          helper={`${Math.round(lessonProgress)}% ${labels.coverage}`}
          details={[
            { label: labels.arabic_items_total, value: stats.arabicItemsIntroduced },
            {
              label: labels.remaining,
              value: Math.max(0, stats.arabicLessonsTotal - stats.arabicLessonsCompleted),
            },
          ]}
        />
        <MetricCard
          label={labels.qada}
          value={stats.qadaCompleted}
          icon={<Iconify icon="solar:check-circle-bold" width={28} />}
          color="success"
          helper={labels.allTime}
          details={[
            {
              label: labels.inLatestReport,
              value: latestReport ? (reportCount(latestReport, 'prayer_completed') ?? '—') : '—',
            },
            { label: labels.weekEnd, value: latestReport?.periodEnd ?? '—' },
          ]}
        />
        <MetricCard
          label={labels.due}
          value={stats.namesDue + stats.arabicDue}
          icon={<Iconify icon="solar:restart-bold" width={28} />}
          color="warning"
          helper={labels.readyForReview}
          details={[
            { label: labels.nameReview, value: stats.namesDue },
            { label: labels.arabicReview, value: stats.arabicDue },
          ]}
        />
      </Box>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        {/* Real quiz counters in the full Minimal AppWidget radial composition. */}
        <Card
          sx={{
            p: { xs: 2.5, md: 3.5 },
            flexDirection: { xs: 'column', sm: 'row' },
            display: 'flex',
            gap: 3,
            alignItems: 'center',
            bgcolor: 'primary.dark',
            color: 'common.white',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Iconify
            aria-hidden
            icon="solar:chart-square-outline"
            sx={{
              position: 'absolute',
              width: 180,
              height: 180,
              right: -55,
              bottom: -40,
              opacity: 0.08,
            }}
          />
          <Box
            sx={{
              width: 112,
              height: 112,
              position: 'relative',
              flexShrink: 0,
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <CircularProgress
              aria-hidden
              variant="determinate"
              value={100}
              size={112}
              thickness={4}
              sx={{ color: 'rgba(255,255,255,0.12)', position: 'absolute' }}
            />
            {stats.totalAnswers > 0 && (
              <CircularProgress
                aria-label={labels.accuracy}
                variant="determinate"
                value={Math.max(0, Math.min(100, stats.accuracy))}
                size={112}
                thickness={4}
                sx={{
                  color: 'primary.light',
                  position: 'absolute',
                  '& .MuiCircularProgress-circle': { strokeLinecap: 'round' },
                }}
              />
            )}
            <Typography variant="h4">{stats.totalAnswers ? `${stats.accuracy}%` : '—'}</Typography>
          </Box>
          <Box sx={{ minWidth: 0, position: 'relative' }}>
            <Typography variant="h6">{labels.accuracy}</Typography>
            <Typography variant="body2" sx={{ mt: 1, opacity: 0.72 }}>
              {stats.totalAnswers
                ? `${stats.correctAnswers} ${labels.correct} / ${stats.totalAnswers} ${labels.answers}`
                : labels.noAnswers}
            </Typography>
          </Box>
        </Card>
        <Card>
          <CardHeader title={labels.retained} subheader={labels.retainedHint} />
          <Box sx={{ p: 3 }}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="baseline"
              spacing={2}
              sx={{ mb: 2 }}
            >
              <Typography variant="h4">
                {stats.namesLearned}
                <Typography component="span" variant="body2" color="text.secondary">
                  {' '}
                  / {stats.namesIntroduced}
                </Typography>
              </Typography>
              <Iconify icon="solar:verified-check-bold" width={28} sx={{ color: 'primary.main' }} />
            </Stack>
            <LinearProgress
              variant="determinate"
              value={Math.max(0, Math.min(100, learnedProgress))}
              sx={{ height: 6, borderRadius: 1 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5 }}>
              {labels.arabic_items_total}: {stats.arabicItemsIntroduced}
            </Typography>
          </Box>
        </Card>
      </Box>
    </Stack>
  );
}
