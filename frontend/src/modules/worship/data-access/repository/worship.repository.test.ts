import { it, vi, expect, describe, beforeEach } from 'vitest';

import { apiClient } from 'src/shared/api';

import { worshipRepository } from './worship.repository.impl';

vi.mock('src/shared/api', () => ({ apiClient: { get: vi.fn(), post: vi.fn() } }));
const summary = {
  current: null,
  manual_pending: 0,
  manual_completed: 0,
  historical_completed: 0,
  historical_configured: false,
  fast_balance: 1,
  manual_queue: [],
  history: [],
};
describe('worship commands', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiClient.post).mockResolvedValue(summary);
  });
  it('forwards the stable queue key instead of an unqualified completion', async () => {
    await worshipRepository.complete('h:2026-05-23:fajr');
    expect(apiClient.post).toHaveBeenCalledWith('qada/complete/', {
      expected_key: 'h:2026-05-23:fajr',
    });
  });
  it('preserves the idempotency token on a retried fast command', async () => {
    const action = {
      action: 'complete' as const,
      amount: 1,
      operationId: '00000000-0000-4000-8000-000000000001',
    };
    await worshipRepository.fast(action);
    await worshipRepository.fast(action);
    for (const call of vi.mocked(apiClient.post).mock.calls)
      expect(call).toEqual([
        'qada/fast/',
        { action: 'complete', amount: 1, operation_id: action.operationId },
      ]);
  });
});
