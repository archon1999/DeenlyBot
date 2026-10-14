import { it, expect } from 'vitest';

import { reportCount, newestReports } from './report-history';

const older = { id: 1, periodStart: '2026-09-28', periodEnd: '2026-10-04', data: { reviews: 5 } };
const newer = { id: 2, periodStart: '2026-10-05', periodEnd: '2026-10-11', data: { reviews: 17 } };

it('orders history without mutating API cache data', () => {
  const reports = [older, newer];
  expect(newestReports(reports)).toEqual([newer, older]);
  expect(reports).toEqual([older, newer]);
});
it('distinguishes missing counters from a real zero', () => {
  expect(reportCount(older, 'arabic_reviews')).toBeUndefined();
  expect(reportCount({ ...older, data: { reviews: 0 } }, 'reviews')).toBe(0);
  expect(reportCount({ ...older, data: { reviews: -1 } }, 'reviews')).toBeUndefined();
  expect(reportCount({ ...older, data: { reviews: NaN } }, 'reviews')).toBeUndefined();
});
