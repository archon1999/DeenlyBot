import { Box, Alert, Stack, Typography } from '@mui/material';

import { QueryState } from 'src/shared/ui/query-state';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useCalendarLabels } from '../../labels';
import { useCalendar } from '../../../application';
import { EventList } from './components/event-list';

export function CalendarPage() {
  const query = useCalendar();
  const labels = useCalendarLabels();
  return (
    <DashboardContent maxWidth="xl">
      <Stack spacing={4}>
        <Box>
          <Typography variant="h4">{labels.title}</Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            {labels.subtitle}
          </Typography>
        </Box>
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {query.data &&
            (query.data.length ? (
              <EventList events={query.data} labels={labels} />
            ) : (
              <Alert severity="info">{labels.empty}</Alert>
            ))}
        </QueryState>
      </Stack>
    </DashboardContent>
  );
}
