import type { Dayjs } from 'dayjs';
import type { DateValidationError } from '@mui/x-date-pickers/models';
import type { PrayerType } from '../../../../domain';
import type { WorshipLabels } from '../../../labels';

import dayjs from 'dayjs';
import { useState } from 'react';

import {
  Alert,
  Stack,
  Button,
  Dialog,
  MenuItem,
  TextField,
  DialogTitle,
  DialogActions,
  DialogContent,
} from '@mui/material';

import { LocalizedDatePicker } from 'src/shared/ui/date-picker';

export function PrayerForm({
  open,
  mode,
  onClose,
  onSubmit,
  busy,
  error,
  labels,
}: {
  open: boolean;
  mode: 'configure' | 'add';
  onClose: () => void;
  onSubmit: (date: string, prayer: PrayerType) => void;
  busy: boolean;
  error: Error | null;
  labels: WorshipLabels;
}) {
  const [date, setDate] = useState<Dayjs | null>(() => dayjs());
  const [dateError, setDateError] = useState<DateValidationError>(null);
  const [prayer, setPrayer] = useState<PrayerType>('fajr');
  return (
    <Dialog open={open} onClose={busy ? undefined : onClose} fullWidth maxWidth="xs">
      <DialogTitle>{mode === 'configure' ? labels.configure : labels.add}</DialogTitle>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (date?.isValid() && !dateError) onSubmit(date.format('YYYY-MM-DD'), prayer);
        }}
      >
        <DialogContent sx={{ pt: 1.5 }}>
          <Stack spacing={3}>
            {mode === 'configure' && <Alert severity="info">{labels.configureHint}</Alert>}
            <LocalizedDatePicker
              label={labels.date}
              value={date}
              onChange={setDate}
              onError={setDateError}
              disableFuture
              disabled={busy}
              slotProps={{
                textField: {
                  required: true,
                  fullWidth: true,
                  helperText: dateError ? labels.dateError : undefined,
                },
              }}
            />
            <TextField
              select
              label={labels.prayer}
              value={prayer}
              onChange={(event) => setPrayer(event.target.value as PrayerType)}
            >
              {(['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'] as const).map((value) => (
                <MenuItem key={value} value={value}>
                  {labels[value]}
                </MenuItem>
              ))}
            </TextField>
            {error && <Alert severity="error">{error.message}</Alert>}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={onClose} disabled={busy}>
            {labels.cancel}
          </Button>
          <Button
            type="submit"
            variant="contained"
            loading={busy}
            disabled={!date?.isValid() || Boolean(dateError)}
          >
            {labels.save}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
