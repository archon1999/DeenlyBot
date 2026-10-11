import type { CalendarLabels } from '../../../labels';
import type { CalendarEvent } from '../../../../domain';

import { Box, Card, Stack, Typography, CardHeader } from '@mui/material';
import {
  Timeline,
  TimelineDot,
  TimelineItem,
  TimelineContent,
  TimelineSeparator,
  TimelineConnector,
  timelineItemClasses,
} from '@mui/lab';

import { useLocale } from 'src/shared/i18n';
import { Iconify } from 'src/shared/ui/iconify';

import { formatCalendarDate, EstimatedDateIndicator } from '../../../shared';

export function EventList({ events, labels }: { events: CalendarEvent[]; labels: CalendarLabels }) {
  const { language } = useLocale();
  const next = events[0];
  const nextDate = formatCalendarDate(next.date, language);
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: 'minmax(0,1.8fr) minmax(0,1fr)' },
        gap: 3,
        alignItems: 'start',
      }}
    >
      {/* Full Minimal reminder/timeline composition; dates are server occurrences. */}
      <Card sx={{ order: { xs: 2, md: 1 } }}>
        <CardHeader title={labels.upcoming} subheader={`${events.length} ${labels.dates}`} />
        <Timeline
          sx={{
            p: { xs: 2.5, md: 3 },
            m: 0,
            [`& .${timelineItemClasses.root}:before`]: { p: 0, flex: 0 },
          }}
        >
          {events.map((event) => {
            const date = formatCalendarDate(event.date, language);
            return (
              <TimelineItem key={event.id}>
                <TimelineSeparator>
                  <TimelineDot color={event.id === next.id ? 'primary' : 'grey'} />
                  {event.id === events[events.length - 1].id ? null : (
                    <TimelineConnector sx={{ bgcolor: 'divider' }} />
                  )}
                </TimelineSeparator>
                <TimelineContent sx={{ pb: 3.5, minWidth: 0 }}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3}>
                    <Box
                      sx={{
                        minWidth: 80,
                        p: 2,
                        borderRadius: 2,
                        bgcolor: event.id === next.id ? 'primary.lighter' : 'background.neutral',
                        color: event.id === next.id ? 'primary.dark' : 'text.primary',
                        textAlign: 'center',
                        alignSelf: 'flex-start',
                      }}
                    >
                      <Typography variant="h4">{date.day}</Typography>
                      <Typography variant="overline">{date.month}</Typography>
                      <Typography variant="caption" display="block" color="text.secondary">
                        {date.year}
                      </Typography>
                    </Box>
                    <Stack spacing={1} flexGrow={1}>
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        flexWrap="wrap"
                        useFlexGap
                      >
                        <Typography variant="h6">{event.title}</Typography>
                        <EstimatedDateIndicator isEstimated={event.isEstimated} />
                      </Stack>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}
                      >
                        {event.description}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {event.hijriYear} · {labels.hijri}
                      </Typography>
                    </Stack>
                  </Stack>
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
      </Card>
      <Stack spacing={3} sx={{ order: { xs: 1, md: 2 } }}>
        <Card
          sx={{
            p: 3.5,
            bgcolor: 'primary.dark',
            color: 'common.white',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Iconify
            aria-hidden
            icon="solar:cloudy-moon-bold-duotone"
            sx={{
              width: 160,
              height: 160,
              right: -45,
              top: -15,
              position: 'absolute',
              opacity: 0.1,
            }}
          />
          <Stack spacing={3} sx={{ position: 'relative' }}>
            <Typography variant="overline" sx={{ opacity: 0.72 }}>
              {labels.next}
            </Typography>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Box
                sx={{
                  p: 1.5,
                  minWidth: 74,
                  borderRadius: 2,
                  bgcolor: 'rgba(255,255,255,0.12)',
                  textAlign: 'center',
                }}
              >
                <Typography variant="h3">{nextDate.day}</Typography>
                <Typography variant="caption" sx={{ textTransform: 'uppercase' }}>
                  {nextDate.month}
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6">{next.title}</Typography>
                <Stack direction="row" alignItems="center" spacing={0.75} sx={{ mt: 0.5 }}>
                  <Typography variant="body2" sx={{ opacity: 0.72 }}>
                    {nextDate.year} · {next.hijriYear} {labels.hijri}
                  </Typography>
                  <EstimatedDateIndicator
                    isEstimated={next.isEstimated}
                    sx={{ color: 'inherit', opacity: 0.72 }}
                  />
                </Stack>
              </Box>
            </Stack>
          </Stack>
        </Card>
        <Card sx={{ p: 3, bgcolor: 'background.neutral' }}>
          <Iconify
            icon="solar:info-circle-bold"
            width={24}
            sx={{ color: 'primary.main', mb: 1.5 }}
          />
          <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
            {labels.hint}
          </Typography>
        </Card>
      </Stack>
    </Box>
  );
}
