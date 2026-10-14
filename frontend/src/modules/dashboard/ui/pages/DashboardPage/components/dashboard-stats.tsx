import type { DashboardLabels } from '../../../labels';
import type { ProgressStats } from 'src/modules/reports';

import { Box } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { MetricCard } from 'src/shared/ui/metric-card';

export function DashboardStats({
  stats,
  labels,
}: {
  stats: ProgressStats;
  labels: DashboardLabels;
}) {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr 1fr', lg: 'repeat(4,1fr)' },
        gap: 2.5,
      }}
    >
      <MetricCard
        label={labels.namesStats}
        value={`${stats.namesIntroduced} / ${stats.namesTotal}`}
        icon={<Iconify icon="solar:notebook-bookmark-linear" width={28} />}
        color="primary"
      />
      <MetricCard
        label={labels.arabicStats}
        value={`${stats.arabicLessonsCompleted} / ${stats.arabicLessonsTotal}`}
        icon={<Iconify icon="solar:letter-linear" width={28} />}
        color="info"
      />
      <MetricCard
        label={labels.accuracy}
        value={stats.totalAnswers ? `${stats.accuracy}%` : '—'}
        helper={stats.totalAnswers ? undefined : labels.noAnswers}
        icon={<Iconify icon="solar:check-circle-linear" width={28} />}
        color="success"
      />
      <MetricCard
        label={labels.qadaStats}
        value={stats.qadaCompleted}
        icon={<Iconify icon="solar:check-circle-linear" width={28} />}
        color="warning"
      />
    </Box>
  );
}
