import { Box, Stack, Typography } from '@mui/material';

import { QueryState } from 'src/shared/ui/query-state';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useSettingsLabels } from '../../labels';
import { useUserSettings } from '../../../application';
import { SettingsForm } from './components/settings-form';

export function SettingsPage() {
  const query = useUserSettings();
  const labels = useSettingsLabels();
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
          {query.data && <SettingsForm initial={query.data} labels={labels} />}
        </QueryState>
      </Stack>
    </DashboardContent>
  );
}
