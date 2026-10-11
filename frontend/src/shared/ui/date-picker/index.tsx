import 'dayjs/locale/ru';
import 'dayjs/locale/uz-latn';

import type { SvgIconProps } from '@mui/material/SvgIcon';
import type { DatePickerProps } from '@mui/x-date-pickers/DatePicker';

import { enUS, ruRU } from '@mui/x-date-pickers/locales';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

import { useLocale } from 'src/shared/i18n';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

const uzLocale: typeof enUS.components.MuiLocalizationProvider.defaultProps.localeText = {
  previousMonth: 'Oldingi oy',
  nextMonth: 'Keyingi oy',
  openPreviousView: 'Oldingi ko‘rinish',
  openNextView: 'Keyingi ko‘rinish',
  calendarViewSwitchingButtonAriaLabel: (view) =>
    view === 'year' ? 'Taqvim ko‘rinishiga o‘tish' : 'Yil ko‘rinishiga o‘tish',
  start: 'Boshlanish',
  end: 'Tugash',
  startDate: 'Boshlanish sanasi',
  endDate: 'Tugash sanasi',
  cancelButtonLabel: 'Bekor qilish',
  clearButtonLabel: 'Tozalash',
  okButtonLabel: 'Tanlash',
  todayButtonLabel: 'Bugun',
  nextStepButtonLabel: 'Keyingi',
  datePickerToolbarTitle: 'Sanani tanlang',
  dateRangePickerToolbarTitle: 'Sana oralig‘ini tanlang',
  calendarWeekNumberHeaderLabel: 'Hafta raqami',
  calendarWeekNumberHeaderText: '#',
  calendarWeekNumberAriaLabelText: (week) => `${week}-hafta`,
  calendarWeekNumberText: (week) => `${week}`,
  openDatePickerDialogue: (date) =>
    date ? `Sanani tanlash, tanlangan sana: ${date}` : 'Sanani tanlash',
  openRangePickerDialogue: (range) =>
    range ? `Sana oralig‘ini tanlash: ${range}` : 'Sana oralig‘ini tanlash',
  fieldClearLabel: 'Tozalash',
  dateTableLabel: 'Sanani tanlash',
  fieldYearPlaceholder: (params) => 'Y'.repeat(params.digitAmount),
  fieldMonthPlaceholder: (params) => (params.contentType === 'letter' ? 'MMMM' : 'MM'),
  fieldDayPlaceholder: () => 'DD',
  fieldWeekDayPlaceholder: (params) => (params.contentType === 'letter' ? 'EEEE' : 'EE'),
  year: 'Yil',
  month: 'Oy',
  day: 'Kun',
  weekDay: 'Hafta kuni',
  empty: 'Bo‘sh',
};

function CalendarIcon({ className, sx }: SvgIconProps) {
  return <OutlineIcon name="calendar" width={22} className={className} sx={sx} />;
}

/** Shared MUI picker keeps all date-entry fields localized consistently. */
export function LocalizedDatePicker(props: DatePickerProps) {
  const { language } = useLocale();
  const localeText =
    language === 'uz'
      ? uzLocale
      : (language === 'ru' ? ruRU : enUS).components.MuiLocalizationProvider.defaultProps
          .localeText;
  return (
    <LocalizationProvider
      dateAdapter={AdapterDayjs}
      adapterLocale={language === 'uz' ? 'uz-latn' : language}
      localeText={localeText}
    >
      <DatePicker
        {...props}
        format={props.format ?? (language === 'en' ? 'MM/DD/YYYY' : 'DD.MM.YYYY')}
        slots={{ openPickerIcon: CalendarIcon, ...props.slots }}
      />
    </LocalizationProvider>
  );
}
