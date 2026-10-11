import type { UserSettings } from '../domain';

import { it, expect, describe } from 'vitest';

import { reconcileSettingsDraft } from './settings-draft';

const baseline: UserSettings = {
  language: 'uz',
  timezone: 'Asia/Tashkent',
  enabled: true,
  randomMessagesPerDay: 2,
  randomWindowStart: '09:00',
  randomWindowEnd: '21:00',
  weeklyReportEnabled: true,
  weeklyReportWeekday: 6,
  weeklyReportTime: '20:00',
};

describe('settings draft reconciliation', () => {
  it('adopts a header language change without discarding an unsaved timezone', () => {
    const draft = { ...baseline, timezone: 'Europe/London' };
    const incoming = { ...baseline, language: 'en' as const, randomMessagesPerDay: 3 };
    const result = reconcileSettingsDraft(draft, baseline, incoming);
    expect(result.language).toBe('en');
    expect(result.timezone).toBe('Europe/London');
    expect(result.randomMessagesPerDay).toBe(3);
  });
  it('preserves intentional local language and notification changes during a refetch', () => {
    const draft = { ...baseline, language: 'ru' as const, enabled: false };
    const incoming = { ...baseline, language: 'en' as const, weeklyReportWeekday: 0 };
    const result = reconcileSettingsDraft(draft, baseline, incoming);
    expect(result.language).toBe('ru');
    expect(result.enabled).toBe(false);
    expect(result.weeklyReportWeekday).toBe(0);
  });
  it('keeps dirty fields through consecutive language changes', () => {
    const russian = { ...baseline, language: 'ru' as const };
    const first = reconcileSettingsDraft(
      { ...baseline, timezone: 'Europe/London' },
      baseline,
      russian
    );
    const english = { ...russian, language: 'en' as const };
    const second = reconcileSettingsDraft(first, russian, english);
    expect(second.language).toBe('en');
    expect(second.timezone).toBe('Europe/London');
  });
});
