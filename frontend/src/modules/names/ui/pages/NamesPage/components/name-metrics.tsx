import type { NamesLabels } from '../../../labels';
import type { NamesOverview } from '../../../../domain';

import { Box } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { MetricCard } from 'src/shared/ui/metric-card';

export function NameMetrics({ data, labels }: { data: NamesOverview; labels: NamesLabels }) {
  return (
    <Box
      sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3,1fr)' }, gap: 2.5 }}
    >
      <MetricCard
        label={labels.introduced}
        value={`${data.introducedCount} / ${data.total}`}
        progress={data.total ? (data.introducedCount / data.total) * 100 : 0}
        icon={<Iconify icon="solar:file-text-bold" width={28} />}
        color="primary"
      />
      <MetricCard
        label={labels.learned}
        value={data.learnedCount}
        icon={<Iconify icon="solar:verified-check-bold" width={28} />}
        color="success"
      />
      <MetricCard
        label={labels.due}
        value={data.dueCount}
        icon={<Iconify icon="solar:restart-bold" width={28} />}
        color="warning"
      />
    </Box>
  );
}
