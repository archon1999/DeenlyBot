import type { CardProps } from '@mui/material/Card';

import { varAlpha } from 'minimal-shared/utils';

import { Box, Card, Stack, Divider, Typography, LinearProgress } from '@mui/material';

type MetricColor = 'primary' | 'secondary' | 'info' | 'success' | 'warning';
type Props = CardProps & {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: MetricColor;
  helper?: string;
  progress?: number;
  details?: { label: string; value: string | number }[];
};

/** Adapted from the supplied full Minimal CourseWidgetSummary, without demo data. */
export function MetricCard({
  label,
  value,
  icon,
  color = 'primary',
  helper,
  progress,
  details,
  sx,
  ...other
}: Props) {
  return (
    <Card
      sx={[
        { p: 3, minWidth: 0, position: 'relative', overflow: 'hidden' },
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
      {...other}
    >
      <Box
        aria-hidden
        sx={(theme) => ({
          position: 'absolute',
          right: -88,
          top: -44,
          width: 160,
          height: 160,
          borderRadius: 3,
          transform: 'rotate(40deg)',
          pointerEvents: 'none',
          background: `linear-gradient(to right, ${varAlpha(theme.vars.palette[color].mainChannel, 0.14)}, transparent)`,
        })}
      />
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
        }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ minWidth: 0 }}>
          {label}
        </Typography>
        {icon && (
          <Box aria-hidden sx={{ flexShrink: 0, color: `${color}.main`, display: 'flex' }}>
            {icon}
          </Box>
        )}
      </Box>
      <Typography variant="h4" sx={{ overflowWrap: 'anywhere' }}>
        {value}
      </Typography>
      {helper && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
          {helper}
        </Typography>
      )}
      {progress !== undefined && (
        <LinearProgress
          color={color}
          variant="determinate"
          value={Math.max(0, Math.min(100, progress))}
          sx={{ mt: 2.5, height: 5 }}
        />
      )}
      {!!details?.length && (
        <Stack spacing={1} sx={{ mt: 2 }}>
          <Divider sx={{ mb: 0.5 }} />
          {details.map((detail) => (
            <Box
              key={detail.label}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
                gap: 1,
              }}
            >
              <Typography variant="caption" color="text.secondary">
                {detail.label}
              </Typography>
              <Typography variant="subtitle2" sx={{ flexShrink: 0 }}>
                {detail.value}
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Card>
  );
}
