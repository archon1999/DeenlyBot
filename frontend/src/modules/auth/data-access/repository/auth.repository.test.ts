import { it, vi, expect, describe, beforeEach } from 'vitest';

import { apiClient } from 'src/shared/api';

import { authRepository } from './auth.repository.impl';

vi.mock('src/shared/api', () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
  ApiError: class extends Error {},
}));

const profile = {
  id: 8,
  first_name: 'Laylo',
  username: '',
  language: 'uz',
  timezone: 'Asia/Tashkent',
  account_kind: 'member',
  is_guest: false,
  email: 'laylo@example.com',
  telegram_linked: false,
};

describe('account command transport', () => {
  beforeEach(() => vi.clearAllMocks());
  it('registers without accepting a client-selected account identity', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ profile });
    const result = await authRepository.register({
      email: 'laylo@example.com',
      password: 'test credential',
      firstName: 'Laylo',
      language: 'uz',
    });
    expect(apiClient.post).toHaveBeenCalledWith('auth/register/', {
      email: 'laylo@example.com',
      password: 'test credential',
      first_name: 'Laylo',
      language: 'uz',
    });
    expect(result.id).toBe(8);
    expect(result.isGuest).toBe(false);
  });
  it('uses the separate authenticated Telegram-link purpose endpoints', async () => {
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({
        telegram_url: 'https://t.me/test_bot?start=web_link',
        expires_at: '2026-10-11T20:00:00Z',
        verification_code: 'ABC012',
      })
      .mockResolvedValueOnce({ status: 'pending' });
    const challenge = await authRepository.startTelegramLink();
    const result = await authRepository.completeTelegramLink();
    expect(apiClient.post).toHaveBeenNthCalledWith(1, 'auth/telegram/link/start/');
    expect(apiClient.post).toHaveBeenNthCalledWith(2, 'auth/telegram/link/complete/');
    expect(challenge.verificationCode).toBe('ABC012');
    expect(result).toEqual({ status: 'pending', profile: null });
  });
  it('updates only requested profile fields and retains server ownership', async () => {
    vi.mocked(apiClient.patch).mockResolvedValue({ profile });
    await authRepository.updateProfile({ firstName: 'Laylo' });
    expect(apiClient.patch).toHaveBeenCalledWith('auth/profile/', { first_name: 'Laylo' });
  });
});
