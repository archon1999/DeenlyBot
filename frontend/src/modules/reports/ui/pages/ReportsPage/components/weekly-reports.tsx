import type { ReportsLabels } from '../../../labels';
import type { WeeklyReport } from '../../../../domain';

import {
  Box,
  Stack,
  Accordion,
  Typography,
  AccordionDetails,
  AccordionSummary,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

const keys = [
  'introduced',
  'learned_total',
  'reviews',
  'correct',
  'accuracy',
  'arabic_lessons_completed',
  'arabic_items_total',
  'arabic_reviews',
  'arabic_accuracy',
  'prayer_completed',
  'fast_completed',
  'favorites_added',
] as const;
export function WeeklyReports({
  reports,
  labels,
}: {
  reports: WeeklyReport[];
  labels: ReportsLabels;
}) {
  return (
    <Stack spacing={2}>
      {reports.map((report, index) => (
        <Accordion
          key={report.id}
          defaultExpanded={index === 0}
          disableGutters
          sx={(theme) => ({
            boxShadow: theme.vars.customShadows.card,
            border: 0,
            borderRadius: 2,
            '&:before': { display: 'none' },
            '&.Mui-expanded': { m: 0 },
          })}
        >
          <AccordionSummary
            expandIcon={<Iconify icon="eva:arrow-ios-downward-fill" />}
            sx={{ px: 2.5, py: 1 }}
          >
            <Stack direction="row" alignItems="center" spacing={2}>
              <Box
                sx={{
                  p: 1.25,
                  borderRadius: 1.5,
                  bgcolor: 'primary.lighter',
                  color: 'primary.main',
                  display: 'flex',
                }}
              >
                <Iconify icon="solar:calendar-date-bold" width={24} />
              </Box>
              <Typography variant="subtitle2">
                {report.periodStart} — {report.periodEnd}
              </Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 2.5, pt: 0 }}>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', sm: 'repeat(2,1fr)', lg: 'repeat(3,1fr)' },
                gap: 1.5,
              }}
            >
              {keys
                .filter((key) => report.data[key] !== undefined)
                .map((key) => (
                  <Stack
                    key={key}
                    spacing={0.5}
                    sx={{ p: 2, borderRadius: 1.5, bgcolor: 'background.neutral' }}
                  >
                    <Typography variant="caption" color="text.secondary">
                      {labels[key]}
                    </Typography>
                    <Typography variant="h6">
                      {report.data[key]}
                      {key.includes('accuracy') ? '%' : ''}
                    </Typography>
                  </Stack>
                ))}
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Stack>
  );
}
