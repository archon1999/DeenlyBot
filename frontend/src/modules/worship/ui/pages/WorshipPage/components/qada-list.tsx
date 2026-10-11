import type { QadaRecord } from '../../../../domain';
import type { WorshipLabels } from '../../../labels';

import { varAlpha } from 'minimal-shared/utils';

import { Box, Alert, Stack, Divider, Typography } from '@mui/material';
import {
  Timeline,
  TimelineDot,
  TimelineItem,
  TimelineContent,
  TimelineSeparator,
  TimelineConnector,
  timelineItemClasses,
} from '@mui/lab';

import { Label } from 'src/shared/ui/label';
import { useLocale } from 'src/shared/i18n';

export function QadaList({
  rows,
  history,
  labels,
}: {
  rows: QadaRecord[];
  history: boolean;
  labels: WorshipLabels;
}) {
  const { language } = useLocale();
  if (!rows.length)
    return <Alert severity="info">{history ? labels.noHistory : labels.noQueue}</Alert>;
  // Adapted from the full Minimal OrderDetailsHistory/AnalyticsOrderTimeline.
  if (history)
    return (
      <Timeline sx={{ p: 0, m: 0, [`& .${timelineItemClasses.root}:before`]: { p: 0, flex: 0 } }}>
        {rows.map((row, index) => (
          <TimelineItem key={row.id}>
            <TimelineSeparator>
              <TimelineDot color={index === 0 ? 'primary' : 'grey'} />
              {index === rows.length - 1 ? null : <TimelineConnector sx={{ bgcolor: 'divider' }} />}
            </TimelineSeparator>
            <TimelineContent sx={{ pb: 3, minWidth: 0 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
                <Typography variant="subtitle2">
                  {labels[row.prayerType]} · {row.prayerDate}
                </Typography>
                <Label color="success">{labels.done}</Label>
              </Stack>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: 'block', mt: 0.5 }}
              >
                {labels[row.source]}
                {row.completedAt
                  ? ` · ${new Date(row.completedAt).toLocaleString(language === 'ru' ? 'ru-RU' : language === 'uz' ? 'uz-UZ' : 'en-US')}`
                  : ''}
              </Typography>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    );
  return (
    <Stack divider={<Divider />} spacing={2}>
      {rows.map((row, index) => (
        <Stack
          key={row.id}
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          spacing={2}
        >
          <Stack direction="row" alignItems="center" spacing={2} sx={{ minWidth: 0 }}>
            <Box
              sx={(theme) => ({
                width: 40,
                height: 40,
                flexShrink: 0,
                borderRadius: 1.5,
                bgcolor:
                  index === 0
                    ? varAlpha(theme.vars.palette.primary.mainChannel, 0.08)
                    : 'background.neutral',
                color: index === 0 ? 'primary.dark' : 'text.secondary',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                typography: 'subtitle2',
                ...theme.applyStyles('dark', {
                  bgcolor:
                    index === 0
                      ? varAlpha(theme.vars.palette.primary.mainChannel, 0.16)
                      : 'background.neutral',
                  color: index === 0 ? 'primary.light' : 'text.secondary',
                }),
              })}
            >
              {index + 1}
            </Box>
            <Box>
              <Typography variant="subtitle1">
                {labels[row.prayerType]} · {row.prayerDate}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {labels[row.source]}
                {history && row.completedAt
                  ? ` · ${new Date(row.completedAt).toLocaleDateString()}`
                  : ''}
              </Typography>
            </Box>
          </Stack>
          <Label color={index === 0 ? 'warning' : 'default'}>{labels.pending}</Label>
        </Stack>
      ))}
    </Stack>
  );
}
