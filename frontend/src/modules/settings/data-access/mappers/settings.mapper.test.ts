import { it, expect, describe } from 'vitest';

import { mapSettings, settingsPayload } from './settings.mapper';

describe('notification settings transport boundary', () => {
  it('round-trips disabled random messages and Monday without replacing zero values', () => {
    const dto = {
      language: 'uz' as const,
      timezone: 'Asia/Tashkent',
      enabled: false,
      random_messages_per_day: 0,
      random_window_start: '09:30:00',
      random_window_end: '18:00:00',
      weekly_report_enabled: true,
      weekly_report_weekday: 0,
      weekly_report_time: '20:15:00',
    };
    expect(settingsPayload(mapSettings(dto))).toEqual(dto);
  });
});
