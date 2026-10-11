import { Box, Stack } from '@mui/material';

import { useSession } from 'src/modules/auth';
import { QueryState } from 'src/shared/ui/query-state';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useDashboardLabels } from '../../labels';
import { useDashboard } from '../../../application';
import { TodayActions } from './components/today-actions';
import { LearningTracks } from './components/learning-tracks';
import { DashboardStats } from './components/dashboard-stats';
import { UpcomingEvents } from './components/upcoming-events';
import { DashboardHeading } from './components/dashboard-heading';
import { LearningOverview } from './components/learning-overview';

export function DashboardPage() {
  const query = useDashboard();
  const labels = useDashboardLabels();
  const { profile } = useSession();
  return (
    <DashboardContent maxWidth="xl">
      <Stack spacing={4}>
        <DashboardHeading labels={labels} />
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {query.data && (
            <>
              <LearningOverview data={query.data} labels={labels} firstName={profile?.firstName} />
              <DashboardStats stats={query.data.stats} labels={labels} />
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', lg: '1.25fr 1fr' },
                  gap: 3,
                  alignItems: 'start',
                }}
              >
                <LearningTracks data={query.data} labels={labels} />
                <TodayActions data={query.data} labels={labels} />
              </Box>
              <UpcomingEvents events={query.data.upcomingEvents} labels={labels} />
            </>
          )}
        </QueryState>
      </Stack>
    </DashboardContent>
  );
}
