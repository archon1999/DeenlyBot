import type { DashboardLabels } from '../../../labels';
import type { CalendarEvent } from 'src/modules/calendar';

import { Link } from 'react-router';

import { Box, Card, Stack, Button, CardHeader, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { EstimatedDateIndicator } from 'src/modules/calendar';

/** Adapted from full Minimal src/sections/overview/course/course-reminders.tsx. */
export function UpcomingEvents({
  events,
  labels,
}: {
  events: CalendarEvent[];
  labels: DashboardLabels;
}) {
  return (
    <Card>
      <CardHeader
        title={labels.upcoming}
        subheader={labels.upcomingRange}
        action={
          <Button
            component={Link}
            to="/calendar"
            size="small"
            endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
            sx={{ mt: 0.5 }}
          >
            {labels.calendar}
          </Button>
        }
      />
      <Box sx={{ p: 3 }}>
        {events.length ? (
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: 'repeat(3,1fr)' },
              gap: 3,
            }}
          >
            {events.map((event) => (
              <Stack key={`${event.id}-${event.date}`} direction="row" spacing={2}>
                <Box
                  sx={{
                    width: 5,
                    borderRadius: 1,
                    bgcolor: 'primary.main',
                    opacity: 0.4,
                    flexShrink: 0,
                  }}
                />
                <Stack spacing={1}>
                  <Typography variant="subtitle1">{event.title}</Typography>
                  <Stack direction="row" spacing={0.75} alignItems="center">
                    <Iconify
                      icon="solar:calendar-date-bold"
                      width={16}
                      sx={{ color: 'text.disabled' }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {event.date}
                    </Typography>
                    <EstimatedDateIndicator isEstimated={event.isEstimated} />
                  </Stack>
                </Stack>
              </Stack>
            ))}
          </Box>
        ) : (
          <Typography color="text.secondary">{labels.noEvents}</Typography>
        )}
      </Box>
    </Card>
  );
}
