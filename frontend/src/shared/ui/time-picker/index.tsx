import 'dayjs/locale/ru';
import 'dayjs/locale/uz-latn';

import type { Dayjs } from 'dayjs';

import { useState, useEffect } from 'react';

import { enUS, ruRU } from '@mui/x-date-pickers/locales';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

import { useLocale } from 'src/shared/i18n';

import { parseTime } from './value';

/** MUI desktop menu / mobile clock, with a local draft for incomplete keyboard input. */
export function LocalizedTimePicker({
  label,
  value,
  onChange,
  onValidityChange,
  minutesStep = 1,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  onValidityChange: (invalid: boolean) => void;
  minutesStep?: number;
}) {
  const { language } = useLocale();
  const [draft, setDraft] = useState<Dayjs | null>(() => parseTime(value));
  useEffect(() => {
    setDraft(parseTime(value));
  }, [value]);
  const uzLocale = {
    cancelButtonLabel: 'Bekor qilish',
    okButtonLabel: 'Tanlash',
    timePickerToolbarTitle: 'Vaqtni tanlang',
    hours: 'Soat',
    minutes: 'Daqiqa',
    fieldHoursPlaceholder: () => 'SS',
    fieldMinutesPlaceholder: () => 'DD',
    openTimePickerDialogue: (time: string | null) =>
      time ? `Vaqtni tanlash: ${time}` : 'Vaqtni tanlash',
    clockLabelText: (view: string) => (view === 'hours' ? 'Soatni tanlang' : 'Daqiqani tanlang'),
    hoursClockNumberText: (hours: string) => `${hours} soat`,
    minutesClockNumberText: (minutes: string) => `${minutes} daqiqa`,
    selectHours: 'Soatni tanlang',
    selectMinutes: 'Daqiqani tanlang',
  };
  return (
    <LocalizationProvider
      dateAdapter={AdapterDayjs}
      adapterLocale={language === 'uz' ? 'uz-latn' : language}
      localeText={
        language === 'uz'
          ? uzLocale
          : (language === 'ru' ? ruRU : enUS).components.MuiLocalizationProvider.defaultProps
              .localeText
      }
    >
      <TimePicker
        label={label}
        value={draft}
        ampm={false}
        format="HH:mm"
        views={['hours', 'minutes']}
        minutesStep={minutesStep}
        timeSteps={{ minutes: minutesStep }}
        onChange={(next, context) => {
          setDraft(next);
          const invalid = !next?.isValid() || context.validationError !== null;
          onValidityChange(invalid);
          if (!invalid && next) onChange(next.format('HH:mm'));
        }}
        onError={(error) => onValidityChange(error !== null)}
        slotProps={{
          textField: { fullWidth: true, required: true },
          actionBar: { actions: ['cancel', 'accept'] },
        }}
      />
    </LocalizationProvider>
  );
}
