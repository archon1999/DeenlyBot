import { it, expect } from 'vitest';

import { parseTime } from './value';

it.each(['00:00', '20:00', '23:59', '08:30:00'])('preserves local wall-clock time %s', (value) => {
  expect(parseTime(value)?.format('HH:mm')).toBe(value.slice(0, 5));
});

it.each(['24:00', '20:60', '2:00', '', 'invalid', '12:30:90', '2026-10-14T20:00'])(
  'rejects invalid time %s',
  (value) => {
    expect(parseTime(value)).toBeNull();
  }
);
