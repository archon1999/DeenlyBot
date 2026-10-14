import { Box, Card, Alert, Stack, Button, Typography, CardHeader } from '@mui/material';

import { QueryState } from 'src/shared/ui/query-state';
import { RouterLink } from 'src/app/routes/components';
import { DeenlyArch } from 'src/shared/ui/deenly-arch';
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
  const stats = query.data?.stats;
  const hasActivity =
    stats &&
    (stats.namesIntroduced > 0 ||
      stats.arabicItemsIntroduced > 0 ||
      stats.arabicLessonsCompleted > 0 ||
      stats.totalAnswers > 0 ||
      stats.qadaCompleted > 0 ||
      Boolean(query.data?.weeklyReports.length));
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
          {query.data && !hasActivity && (
            <Card sx={{ p: { xs: 3, md: 5 }, position: 'relative', overflow: 'hidden' }}>
              <DeenlyArch
                sx={{ position: 'absolute', right: -20, bottom: -70, width: 220, height: 275 }}
              />
              <Stack spacing={2} sx={{ position: 'relative', maxWidth: 560 }}>
                <Typography variant="h5">{labels.firstStep}</Typography>
                <Typography color="text.secondary">{labels.firstStepHint}</Typography>
                <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1.5}>
                  <Button component={RouterLink} href="/names" variant="contained">
                    {labels.namesGroup}
                  </Button>
                  <Button component={RouterLink} href="/arabic" variant="outlined">
                    {labels.arabicGroup}
                  </Button>
                </Stack>
              </Stack>
            </Card>
          )}
          {query.data && hasActivity && (
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
