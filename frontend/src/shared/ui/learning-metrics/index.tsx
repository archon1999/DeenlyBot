import type { ComponentProps } from 'react';

import { Box } from '@mui/material';

import { MetricCard } from 'src/shared/ui/metric-card';

export type LearningMetric = Pick<
  ComponentProps<typeof MetricCard>,
  'label' | 'value' | 'icon' | 'color' | 'helper' | 'progress'
>;

/** Common three-card learning overview, independent of feature domain data. */
export function LearningMetrics({
  items,
}: {
  items: [LearningMetric, LearningMetric, LearningMetric];
}) {
  return (
    <Box
      sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3,1fr)' }, gap: 2.5 }}
    >
      {items.map((item) => (
        <MetricCard key={item.label} {...item} />
      ))}
    </Box>
  );
}
