import type { LibraryLabels } from '../../../labels';
import type { LibraryPracticeStats } from '../../../../domain';

import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { LearningMetrics } from 'src/shared/ui/learning-metrics';

export function LibraryProgress({
  stats,
  labels,
}: {
  stats: LibraryPracticeStats;
  labels: LibraryLabels;
}) {
  return (
    <LearningMetrics
      items={[
        {
          label: labels.studied,
          value: `${stats.studiedCount} / ${stats.totalCount}`,
          progress: stats.totalCount ? (stats.studiedCount / stats.totalCount) * 100 : 0,
          color: 'success',
          icon: <OutlineIcon name="check" width={28} />,
        },
        {
          label: labels.accuracy,
          value: stats.answers ? `${stats.accuracy}%` : '—',
          color: 'primary',
          icon: <OutlineIcon name="library" width={28} />,
        },
        {
          label: labels.due,
          value: stats.dueCount,
          color: 'warning',
          icon: <OutlineIcon name="review" width={28} />,
        },
      ]}
    />
  );
}
