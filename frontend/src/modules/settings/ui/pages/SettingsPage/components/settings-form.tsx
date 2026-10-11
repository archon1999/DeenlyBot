import type { SettingsLabels } from '../../../labels';
import type { UserSettings } from '../../../../domain';

import {
  Box,
  Card,
  Grid,
  Alert,
  Stack,
  Button,
  Switch,
  Divider,
  MenuItem,
  TextField,
  Typography,
  ListItemText,
  FormControlLabel,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

import { useSaveSettings, useSettingsDraft } from '../../../../application';

const slots = Array.from(
  { length: 48 },
  (_, i) => `${String(Math.floor(i / 2)).padStart(2, '0')}:${i % 2 ? '30' : '00'}`
);
export function SettingsForm({
  initial,
  labels,
}: {
  initial: UserSettings;
  labels: SettingsLabels;
}) {
  const { values, setValues } = useSettingsDraft(initial);
  const mutation = useSaveSettings();
  const invalidTimezone = mutation.error?.message === 'timezone: Unknown IANA timezone';
  const set = <K extends keyof UserSettings>(key: K, value: UserSettings[K]) => {
    mutation.reset();
    setValues((current) => ({ ...current, [key]: value }));
  };
  return (
    <Stack
      component="form"
      spacing={3}
      onSubmit={(event) => {
        event.preventDefault();
        mutation.mutate(values, {
          onSuccess: (data) => {
            setValues(data);
          },
        });
      }}
    >
      <Card sx={{ p: { xs: 2.5, md: 4 } }}>
        <Stack spacing={4} divider={<Divider sx={{ borderStyle: 'dashed' }} />}>
          <SettingsSection
            title={labels.profile}
            caption={labels.profileHint}
            icon={<Iconify icon="solar:user-rounded-bold" width={28} />}
          >
            <Box
              sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}
            >
              <TextField
                select
                label={labels.language}
                value={values.language}
                onChange={(event) =>
                  set('language', event.target.value as UserSettings['language'])
                }
              >
                <MenuItem value="uz">O‘zbekcha</MenuItem>
                <MenuItem value="ru">Русский</MenuItem>
                <MenuItem value="en">English</MenuItem>
              </TextField>
              <TextField
                label={labels.timezone}
                value={values.timezone}
                onChange={(event) => set('timezone', event.target.value)}
                helperText={labels.timezoneHint}
                error={invalidTimezone}
                required
              />
            </Box>
          </SettingsSection>
          <SettingsSection
            title={labels.notifications}
            caption={labels.notificationsHint}
            icon={<Iconify icon="solar:bell-bing-bold" width={28} />}
          >
            <Stack spacing={3}>
              <FormControlLabel
                control={
                  <Switch checked={values.enabled} onChange={(_, value) => set('enabled', value)} />
                }
                label={labels.enabled}
                labelPlacement="start"
                sx={{ m: 0, justifyContent: 'space-between', gap: 2 }}
              />
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: 'repeat(3,1fr)' },
                  gap: 2,
                }}
              >
                <TextField
                  type="number"
                  label={labels.count}
                  value={values.randomMessagesPerDay}
                  onChange={(event) => set('randomMessagesPerDay', Number(event.target.value))}
                  slotProps={{ htmlInput: { min: 0, max: 10 } }}
                  required
                />
                <TextField
                  select
                  label={labels.start}
                  value={values.randomWindowStart.slice(0, 5)}
                  onChange={(event) => set('randomWindowStart', event.target.value)}
                >
                  {slots.map((time) => (
                    <MenuItem key={time} value={time}>
                      {time}
                    </MenuItem>
                  ))}
                </TextField>
                <TextField
                  select
                  label={labels.end}
                  value={values.randomWindowEnd.slice(0, 5)}
                  onChange={(event) => set('randomWindowEnd', event.target.value)}
                >
                  {slots.map((time) => (
                    <MenuItem key={time} value={time}>
                      {time}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {labels.windowHint}
              </Typography>
            </Stack>
          </SettingsSection>
          <SettingsSection
            title={labels.weekly}
            caption={labels.weeklyHint}
            icon={<Iconify icon="solar:chart-square-outline" width={28} />}
          >
            <Stack spacing={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={values.weeklyReportEnabled}
                    onChange={(_, value) => set('weeklyReportEnabled', value)}
                  />
                }
                label={labels.weeklyEnabled}
                labelPlacement="start"
                sx={{ m: 0, justifyContent: 'space-between', gap: 2 }}
              />
              <Box
                sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}
              >
                <TextField
                  select
                  label={labels.weekday}
                  value={values.weeklyReportWeekday}
                  onChange={(event) => set('weeklyReportWeekday', Number(event.target.value))}
                >
                  {(
                    [
                      'monday',
                      'tuesday',
                      'wednesday',
                      'thursday',
                      'friday',
                      'saturday',
                      'sunday',
                    ] as const
                  ).map((day, index) => (
                    <MenuItem key={day} value={index}>
                      {labels[day]}
                    </MenuItem>
                  ))}
                </TextField>
                <TextField
                  type="time"
                  label={labels.time}
                  value={values.weeklyReportTime.slice(0, 5)}
                  onChange={(event) => set('weeklyReportTime', event.target.value)}
                  slotProps={{ inputLabel: { shrink: true }, htmlInput: { step: 60 } }}
                  required
                />
              </Box>
            </Stack>
          </SettingsSection>
        </Stack>
      </Card>
      {mutation.error && (
        <Alert severity="error">
          {invalidTimezone ? labels.invalidTimezone : mutation.error.message}
        </Alert>
      )}
      {mutation.isSuccess && <Alert severity="success">{labels.saved}</Alert>}
      <Button
        variant="contained"
        type="submit"
        size="large"
        loading={mutation.isPending}
        startIcon={<Iconify icon="eva:checkmark-fill" />}
        sx={{ alignSelf: 'flex-end' }}
      >
        {labels.save}
      </Button>
    </Stack>
  );
}

// Full Minimal AccountNotifications group layout with Deenly's existing controls.
function SettingsSection({
  title,
  caption,
  icon,
  children,
}: {
  title: string;
  caption: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 4 }}>
        <Stack spacing={1.5} sx={{ pr: { md: 3 } }}>
          <Box sx={{ display: 'flex', color: 'primary.main' }}>{icon}</Box>
          <ListItemText
            primary={title}
            secondary={caption}
            slotProps={{
              primary: { sx: { typography: 'h6' } },
              secondary: { sx: { mt: 1, lineHeight: 1.8 } },
            }}
          />
        </Stack>
      </Grid>
      <Grid size={{ xs: 12, md: 8 }}>
        <Box
          sx={{
            p: { xs: 2, sm: 3 },
            borderRadius: 2,
            bgcolor: 'background.neutral',
            '& .MuiInputBase-root': { bgcolor: 'background.paper' },
          }}
        >
          {children}
        </Box>
      </Grid>
    </Grid>
  );
}
