import type { ArabicLabels } from '../../../labels';
import type { ArabicStats } from '../../../../domain';

import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { LearningMetrics } from 'src/shared/ui/learning-metrics';

export function ArabicProgress({ stats, labels }: { stats: ArabicStats; labels: ArabicLabels }) {
  return (
    <LearningMetrics
      items={[
        {
          label: labels.completed,
          value: `${stats.completedLessons} / ${stats.totalLessons}`,
          progress: stats.totalLessons ? (stats.completedLessons / stats.totalLessons) * 100 : 0,
          color: 'success',
          icon: <OutlineIcon name="check" width={28} />,
        },
        {
          label: labels.intro,
          value: stats.introducedItems,
          color: 'primary',
          icon: <OutlineIcon name="arabic" width={28} />,
        },
        {
          label: labels.due,
          value: stats.dueItems,
          color: 'warning',
          icon: <OutlineIcon name="review" width={28} />,
        },
      ]}
    />
  );
}
