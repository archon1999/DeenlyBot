import { Box, Card, Alert, Stack, Typography, CardHeader } from '@mui/material';

import { QueryState } from 'src/shared/ui/query-state';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useReportsLabels } from '../../labels';
import { newestReports } from '../../../domain';
import { useReports } from '../../../application';
import { ProgressCards } from './components/progress-cards';
import { WeeklyReports } from './components/weekly-reports';
import { ReportInsights } from './components/report-insights';

export function ReportsPage() {
  const query = useReports();
  const labels = useReportsLabels();
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
          {query.data && (
            <>
              <ProgressCards
                stats={query.data.stats}
                labels={labels}
                latestReport={newestReports(query.data.weeklyReports)[0]}
              />
              <ReportInsights
                reports={query.data.weeklyReports}
                stats={query.data.stats}
                labels={labels}
              />
              <Card>
                <CardHeader title={labels.weekly} subheader={labels.weeklyHint} />
                <Box sx={{ p: { xs: 2.5, md: 3 } }}>
                  {query.data.weeklyReports.length ? (
                    <WeeklyReports reports={query.data.weeklyReports} labels={labels} />
                  ) : (
                    <Alert severity="info">{labels.empty}</Alert>
                  )}
                </Box>
              </Card>
            </>
          )}
        </QueryState>
      </Stack>
    </DashboardContent>
  );
}
