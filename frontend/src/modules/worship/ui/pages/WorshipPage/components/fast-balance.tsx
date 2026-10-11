import type { WorshipLabels } from '../../../labels';

import { useState } from 'react';

import { Box, Card, Alert, Stack, Button, TextField, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

import { useFastAction } from '../../../../application';

export function FastBalance({ balance, labels }: { balance: number; labels: WorshipLabels }) {
  const mutation = useFastAction();
  const [amount, setAmount] = useState(1);
  const perform = (action: 'add' | 'complete') => {
    const value = action === 'add' ? amount : 1;
    mutation.mutate({ action, amount: value });
  };
  return (
    <Card sx={{ p: { xs: 3, md: 4 } }}>
      <Stack spacing={2.5}>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Box
            sx={{
              p: 1.25,
              display: 'flex',
              color: 'primary.main',
              bgcolor: 'primary.lighter',
              borderRadius: 2,
            }}
          >
            <Iconify icon="solar:calendar-date-bold" width={24} />
          </Box>
          <Typography variant="h6">{labels.fast}</Typography>
        </Stack>
        <Typography variant="h3">
          {balance}{' '}
          <Typography component="span" color="text.secondary" variant="body1">
            {labels.days}
          </Typography>
        </Typography>
        <Typography color="text.secondary" variant="body2">
          {labels.fastHint}
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <TextField
            type="number"
            size="small"
            label={labels.amount}
            value={amount}
            onChange={(event) => setAmount(Number(event.target.value))}
            slotProps={{ htmlInput: { min: 1, max: 10000 } }}
            sx={{ width: { sm: 140 } }}
          />
          <Button
            variant="outlined"
            disabled={!Number.isInteger(amount) || amount < 1 || mutation.isPending}
            onClick={() => perform('add')}
            startIcon={<Iconify icon="solar:add-circle-bold" />}
          >
            {labels.addFast}
          </Button>
        </Stack>
        <Button
          variant="contained"
          loading={mutation.isPending && mutation.variables?.action === 'complete'}
          disabled={balance < 1 || mutation.isPending}
          onClick={() => perform('complete')}
          startIcon={<Iconify icon="eva:checkmark-fill" />}
          sx={{ alignSelf: 'flex-start' }}
        >
          {labels.completeFast}
        </Button>
        {mutation.error && <Alert severity="error">{mutation.error.message}</Alert>}
      </Stack>
    </Card>
  );
}
