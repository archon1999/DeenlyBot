import { it, expect, describe } from 'vitest';

import { formatCalendarDate } from './format-calendar-date';

describe('localized calendar dates', () => {
  it('uses Uzbek month names even when the browser has incomplete Uzbek ICU data', () => {
    expect(formatCalendarDate('2027-02-13', 'uz')).toEqual({
      day: '13',
      month: 'fevral',
      year: '2027',
    });
    expect(formatCalendarDate('2027-03-09', 'uz').month).toBe('mart');
    expect(formatCalendarDate('2026-10-11', 'uz').month).toBe('oktabr');
  });
  it('formats Russian and English month names consistently', () => {
    expect(formatCalendarDate('2027-02-13', 'ru').month).toBe('февр.');
    expect(formatCalendarDate('2027-02-13', 'en').month).toBe('Feb');
  });
  it('preserves a date-only year boundary independent of the browser timezone', () => {
    expect(formatCalendarDate('2026-12-31', 'en')).toEqual({
      day: '31',
      month: 'Dec',
      year: '2026',
    });
    expect(formatCalendarDate('invalid', 'uz')).toEqual({ day: '—', month: '—', year: '—' });
  });
});
