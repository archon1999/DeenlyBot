import type { PrayerType } from '../../../domain';

import { useState } from 'react';

import { Box, Stack, Button, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { QueryState } from 'src/shared/ui/query-state';
import { MetricCard } from 'src/shared/ui/metric-card';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useWorshipLabels } from '../../labels';
import { PrayerForm } from './components/prayer-form';
import { FastBalance } from './components/fast-balance';
import { CurrentQadaCard } from './components/current-qada';
import { QadaRecordTabs } from './components/qada-record-tabs';
import { useQada, useAddQada, useCompleteQada, useConfigureQada } from '../../../application';

export function WorshipPage() {
  const labels = useWorshipLabels();
  const query = useQada();
  const add = useAddQada();
  const configure = useConfigureQada();
  const complete = useCompleteQada();
  const [dialog, setDialog] = useState<'configure' | 'add' | null>(null);
  const data = query.data;
  const close = () => {
    setDialog(null);
    add.reset();
    configure.reset();
  };
  const submit = (date: string, prayer: PrayerType) => {
    if (dialog === 'configure')
      configure.mutate({ startDate: date, startPrayer: prayer }, { onSuccess: close });
    else add.mutate({ prayerDate: date, prayerType: prayer }, { onSuccess: close });
  };
  return (
    <DashboardContent maxWidth="xl">
      <Stack spacing={4}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          justifyContent="space-between"
          alignItems={{ sm: 'center' }}
          spacing={2}
        >
          <Box>
            <Typography variant="h4">{labels.title}</Typography>
            <Typography color="text.secondary" sx={{ mt: 1 }}>
              {labels.subtitle}
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Iconify icon="solar:add-circle-bold" />}
            onClick={() => setDialog('add')}
          >
            {labels.add}
          </Button>
        </Stack>
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {data && (
            <>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
                  gap: 3,
                }}
              >
                <MetricCard
                  label={labels.pending}
                  value={data.manualPending}
                  icon={<Iconify icon="solar:clock-circle-bold" width={28} />}
                  color="warning"
                />
                <MetricCard
                  label={labels.manualDone}
                  value={data.manualCompleted}
                  icon={<Iconify icon="solar:check-circle-bold" width={28} />}
                  color="primary"
                />
                <MetricCard
                  label={labels.historicalDone}
                  value={data.historicalCompleted}
                  icon={<Iconify icon="solar:sort-by-time-bold-duotone" width={28} />}
                  color="info"
                />
              </Box>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', md: '1.45fr 1fr' },
                  gap: 3,
                }}
              >
                <CurrentQadaCard
                  current={data.current}
                  labels={labels}
                  busy={complete.isPending}
                  error={complete.error}
                  onConfigure={
                    !data.historicalConfigured ? () => setDialog('configure') : undefined
                  }
                  onComplete={() => {
                    if (data.current)
                      complete.mutate(data.current.key, { onError: () => query.refetch() });
                  }}
                />
                <FastBalance balance={data.fastBalance} labels={labels} />
              </Box>
              <QadaRecordTabs
                manualQueue={data.manualQueue}
                history={data.history}
                labels={labels}
              />
            </>
          )}
        </QueryState>
        <PrayerForm
          open={dialog !== null}
          mode={dialog ?? 'add'}
          labels={labels}
          onClose={close}
          onSubmit={submit}
          busy={add.isPending || configure.isPending}
          error={dialog === 'configure' ? configure.error : add.error}
        />
      </Stack>
    </DashboardContent>
  );
}
