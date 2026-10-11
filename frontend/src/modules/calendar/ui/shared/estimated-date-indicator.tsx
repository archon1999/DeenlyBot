import type { Theme, SxProps } from '@mui/material/styles';

import { Tooltip, IconButton } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

import { useCalendarLabels } from '../labels';

export function EstimatedDateIndicator({
  isEstimated,
  sx,
}: {
  isEstimated: boolean;
  sx?: SxProps<Theme>;
}) {
  const labels = useCalendarLabels();
  if (!isEstimated) return null;

  return (
    <Tooltip
      arrow
      describeChild
      placement="top"
      title={`${labels.estimated}. ${labels.hint}`}
      enterDelay={200}
      enterTouchDelay={0}
      leaveTouchDelay={5000}
    >
      <IconButton
        size="small"
        aria-label={labels.estimated}
        sx={[
          { width: 24, height: 24, p: 0.5, color: 'text.secondary', flexShrink: 0 },
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
      >
        <Iconify icon="eva:info-outline" width={16} aria-hidden />
      </IconButton>
    </Tooltip>
  );
}
