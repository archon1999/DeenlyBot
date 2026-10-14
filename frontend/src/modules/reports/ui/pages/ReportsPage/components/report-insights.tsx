import type { ReportsLabels } from '../../../labels';
import type { WeeklyReport, ProgressStats } from '../../../../domain';

import { Box, Card, Stack, Button, CardHeader, Typography, LinearProgress } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { Iconify } from 'src/shared/ui/iconify';
import { RouterLink } from 'src/app/routes/components';
import { learningCover } from 'src/shared/ui/learning-cover';

import { reportPeriod } from './weekly-reports';
import { reportCount, newestReports } from '../../../../domain';

export function ReportInsights({
  reports,
  stats,
  labels,
}: {
  reports: WeeklyReport[];
  stats: ProgressStats;
  labels: ReportsLabels;
}) {
  const { language } = useLocale();
  const history = newestReports(reports).slice(0, 6).reverse();
  const max = Math.max(
    1,
    ...history.flatMap((r) => [
      reportCount(r, 'reviews') ?? 0,
      reportCount(r, 'arabic_reviews') ?? 0,
    ])
  );
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', lg: 'minmax(0, 1.6fr) minmax(0, 1fr)' },
        gap: 3,
      }}
    >
      <Card>
        <CardHeader title={labels.trends} subheader={labels.trendsHint} />
        <Stack spacing={2.5} sx={{ p: 3 }}>
          {!history.length && (
            <Typography variant="body2" color="text.secondary">
              {labels.empty}
            </Typography>
          )}
          {history.map((report) => (
            <Box key={report.id}>
              <Typography variant="caption" color="text.secondary">
                {reportPeriod(report, language)}
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                {(
                  [
                    { key: 'reviews', title: labels.namesTests, color: 'primary' },
                    { key: 'arabic_reviews', title: labels.arabicTests, color: 'info' },
                  ] as const
                ).map((series) => (
                  <Box
                    key={series.key}
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: '64px minmax(0,1fr) 32px',
                      gap: 1,
                      alignItems: 'center',
                    }}
                  >
                    <Typography variant="caption" color="text.secondary">
                      {series.title}
                    </Typography>
                    <LinearProgress
                      aria-label={`${reportPeriod(report, language)} · ${series.title}`}
                      aria-valuetext={`${reportCount(report, series.key) ?? '—'} ${series.title}`}
                      aria-hidden={reportCount(report, series.key) === undefined}
                      color={series.color}
                      variant="determinate"
                      value={((reportCount(report, series.key) ?? 0) / max) * 100}
                      sx={{ height: 6, borderRadius: 1 }}
                    />
                    <Typography variant="subtitle2" textAlign="right">
                      {reportCount(report, series.key) ?? '—'}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Box>
          ))}
        </Stack>
      </Card>
      <Card>
        <CardHeader title={labels.reviewPlan} subheader={labels.reviewPlanHint} />
        <Stack spacing={2} sx={{ p: 3 }}>
          {[
            {
              label: labels.nameReview,
              count: stats.namesDue,
              href: '/names',
              tone: 'mint' as const,
            },
            {
              label: labels.arabicReview,
              count: stats.arabicDue,
              href: '/arabic',
              tone: 'blue' as const,
            },
          ].map((item) => (
            <Box
              key={item.href}
              sx={(theme) => ({ ...learningCover(theme, item.tone), p: 2, borderRadius: 2 })}
            >
              <Stack
                direction="row"
                alignItems="baseline"
                justifyContent="space-between"
                spacing={1}
              >
                <Typography variant="subtitle2">{item.label}</Typography>
                <Typography variant="h4">{item.count}</Typography>
              </Stack>
              <Button
                component={RouterLink}
                href={item.href}
                size="small"
                endIcon={<Iconify icon="solar:arrow-right-linear" width={16} />}
                sx={{ mt: 1, px: 0 }}
              >
                {labels.openReview}
              </Button>
            </Box>
          ))}
        </Stack>
      </Card>
    </Box>
  );
}
