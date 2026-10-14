import type { ReportsLabels } from '../../../labels';
import type { WeeklyReport } from '../../../../domain';

import {
  Box,
  Chip,
  Stack,
  Accordion,
  Typography,
  LinearProgress,
  AccordionDetails,
  AccordionSummary,
} from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { Iconify } from 'src/shared/ui/iconify';
import { formatDateParts } from 'src/shared/lib/format-date';
import { learningCover } from 'src/shared/ui/learning-cover';

import { reportCount, newestReports } from '../../../../domain';

export function reportPeriod(report: WeeklyReport, language: 'uz' | 'ru' | 'en') {
  const start = formatDateParts(report.periodStart, language);
  const end = formatDateParts(report.periodEnd, language);
  if (start.year === '—' || end.year === '—') return '—';
  if (start.year === end.year && start.month === end.month)
    return `${start.day}–${end.day} ${end.month} ${end.year}`;
  return `${start.day} ${start.month}${start.year === end.year ? '' : ` ${start.year}`} — ${end.day} ${end.month} ${end.year}`;
}

export function WeeklyReports({
  reports,
  labels,
}: {
  reports: WeeklyReport[];
  labels: ReportsLabels;
}) {
  const { language } = useLocale();
  return (
    <Stack spacing={2}>
      {newestReports(reports).map((report, index) => (
        <Accordion
          key={report.id}
          defaultExpanded={index === 0}
          disableGutters
          sx={{
            boxShadow: 'none',
            bgcolor: 'transparent',
            '&:before': { display: 'none' },
            '&.Mui-expanded': { m: 0 },
          }}
        >
          <AccordionSummary
            expandIcon={<Iconify icon="solar:alt-arrow-down-linear" />}
            sx={{ px: 0, py: 1 }}
          >
            <Stack direction="row" alignItems="center" spacing={1.5} sx={{ minWidth: 0 }}>
              <Box
                sx={(theme) => ({
                  ...learningCover(theme, 'mint'),
                  p: 1.25,
                  borderRadius: 1.5,
                  display: 'flex',
                  flexShrink: 0,
                })}
              >
                <Iconify icon="solar:calendar-mark-linear" width={24} />
              </Box>
              <Box>
                <Typography variant="subtitle2">{reportPeriod(report, language)}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {labels.week}
                </Typography>
              </Box>
              {index === 0 && (
                <Chip
                  label={labels.latest}
                  size="small"
                  variant="soft"
                  sx={{ display: { xs: 'none', sm: 'inline-flex' } }}
                />
              )}
            </Stack>
          </AccordionSummary>
          <AccordionDetails sx={{ px: 0, pb: 2, pt: 1 }}>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: 'repeat(3,1fr)' },
                gap: 2,
              }}
            >
              <ReportGroup
                report={report}
                labels={labels}
                title={labels.namesGroup}
                tone="mint"
                icon="solar:notebook-bookmark-linear"
                primary="reviews"
                rows={['introduced', 'correct']}
                accuracy="accuracy"
                snapshot="learned_total"
              />
              <ReportGroup
                report={report}
                labels={labels}
                title={labels.arabicGroup}
                tone="blue"
                icon="solar:text-square-linear"
                primary="arabic_lessons_completed"
                rows={['arabic_reviews']}
                accuracy="arabic_accuracy"
                snapshot="arabic_items_total"
              />
              <ReportGroup
                report={report}
                labels={labels}
                title={labels.worshipGroup}
                tone="peach"
                icon="solar:checklist-minimalistic-linear"
                primary="prayer_completed"
                rows={['fast_completed', 'favorites_added']}
              />
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Stack>
  );
}

function ReportGroup({
  report,
  labels,
  title,
  tone,
  icon,
  primary,
  rows,
  accuracy,
  snapshot,
}: {
  report: WeeklyReport;
  labels: ReportsLabels;
  title: string;
  tone: Parameters<typeof learningCover>[1];
  icon: React.ComponentProps<typeof Iconify>['icon'];
  primary: keyof ReportsLabels;
  rows: (keyof ReportsLabels)[];
  accuracy?: keyof ReportsLabels;
  snapshot?: keyof ReportsLabels;
}) {
  const value = (key: string) => reportCount(report, key) ?? '—';
  const attempts = reportCount(report, accuracy === 'accuracy' ? 'reviews' : 'arabic_reviews');
  const rate = accuracy && attempts ? reportCount(report, accuracy) : undefined;
  return (
    <Stack
      spacing={1.5}
      sx={(theme) => ({ ...learningCover(theme, tone), p: 2.5, borderRadius: 2, minWidth: 0 })}
    >
      <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
        <Typography variant="subtitle2">{title}</Typography>
        <Iconify icon={icon} width={22} />
      </Stack>
      <Box>
        <Typography variant="h3" sx={{ color: 'text.primary' }}>
          {value(primary)}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {labels[primary]}
        </Typography>
      </Box>
      {rows.map((key) => (
        <Stack
          key={key}
          direction="row"
          justifyContent="space-between"
          alignItems="baseline"
          spacing={1}
        >
          <Typography variant="caption" color="text.secondary">
            {labels[key]}
          </Typography>
          <Typography variant="subtitle2" color="text.primary">
            {value(key)}
          </Typography>
        </Stack>
      ))}
      {accuracy && (
        <Box sx={{ pt: 0.5 }}>
          <Stack direction="row" justifyContent="space-between" spacing={1}>
            <Typography variant="caption" color="text.secondary">
              {labels[accuracy]}
            </Typography>
            <Typography variant="subtitle2" color="text.primary">
              {rate === undefined ? '—' : `${rate}%`}
            </Typography>
          </Stack>
          <LinearProgress
            aria-label={labels[accuracy]}
            aria-hidden={rate === undefined}
            variant="determinate"
            value={Math.min(100, rate ?? 0)}
            sx={{ mt: 1, height: 4, bgcolor: 'action.hover' }}
          />
          {attempts === 0 && (
            <Typography variant="caption" color="text.secondary">
              {labels.noTestsWeek}
            </Typography>
          )}
        </Box>
      )}
      {snapshot && (
        <Box sx={{ pt: 1, mt: 'auto' }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            {labels.snapshot}
          </Typography>
          <Typography variant="caption" color="text.primary">
            {labels[snapshot]}: <strong>{value(snapshot)}</strong>
          </Typography>
        </Box>
      )}
    </Stack>
  );
}
