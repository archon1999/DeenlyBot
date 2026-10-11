import { it, expect, describe } from 'vitest';

import { mapQada } from './worship.mapper';

describe('qada transport boundary', () => {
  it('preserves server queue order and the exact stale-command key', () => {
    const summary = mapQada({
      current: { key: 'm:902', source: 'manual', prayer_date: '2026-10-11', prayer_type: 'isha' },
      manual_pending: 2,
      manual_completed: 4,
      historical_completed: 7,
      historical_configured: true,
      fast_balance: 3,
      manual_queue: [
        {
          id: 902,
          source: 'manual',
          prayer_date: '2026-10-11',
          prayer_type: 'isha',
          status: 'pending',
          completed_at: null,
        },
        {
          id: 901,
          source: 'manual',
          prayer_date: '2026-10-10',
          prayer_type: 'fajr',
          status: 'pending',
          completed_at: null,
        },
      ],
      history: [],
    });
    expect(summary.current?.key).toBe('m:902');
    expect(summary.manualQueue.map((item) => item.id)).toEqual([902, 901]);
    expect(summary.fastBalance).toBe(3);
    expect(summary.historicalConfigured).toBe(true);
  });
  it('represents an unconfigured empty queue without inventing historical debt', () => {
    const summary = mapQada({
      current: null,
      manual_pending: 0,
      manual_completed: 0,
      historical_completed: 0,
      historical_configured: false,
      fast_balance: 0,
      manual_queue: [],
      history: [],
    });
    expect(summary.current).toBeNull();
    expect(summary.historicalConfigured).toBe(false);
  });
});
