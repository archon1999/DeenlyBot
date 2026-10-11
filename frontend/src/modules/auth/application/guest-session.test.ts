import type { Profile, AuthSession, AuthRepository } from '../domain';

import { it, vi, expect } from 'vitest';

import { ApiError } from 'src/shared/api';

import {
  enterGuestOnce,
  enterMiniAppOnce,
  readEntrySession,
  shouldEnterGuest,
} from './guest-session';

const guest: Profile = {
  id: 7,
  firstName: '',
  username: '',
  language: 'uz',
  timezone: 'Asia/Tashkent',
  accountKind: 'guest',
  isGuest: true,
  email: '',
  telegramLinked: false,
};
const anonymous: AuthSession = { authenticated: false, profile: null, botUsername: 'deenlybot' };
const repository = () =>
  ({
    session: vi.fn().mockResolvedValue(anonymous),
    guest: vi.fn().mockResolvedValue(guest),
  }) as unknown as AuthRepository;

it('auto-enters only after a confirmed anonymous response and outside explicitlogin', () => {
  expect(shouldEnterGuest(true, anonymous, null)).toBe(true);
  expect(shouldEnterGuest(false, anonymous, null)).toBe(false);
  expect(shouldEnterGuest(true, undefined, null)).toBe(false);
  expect(shouldEnterGuest(true, { ...anonymous, authenticated: true, profile: guest }, null)).toBe(
    false
  );
});
it('treats401 as anonymous without treating403/500/network failures as guest authorization', async () => {
  const auth = repository();
  vi.mocked(auth.session).mockRejectedValue(new ApiError(401, { detail: 'Anonymous' }));
  expect((await readEntrySession(auth)).authenticated).toBe(false);
  for (const status of [403, 500]) {
    const error = new ApiError(status, { detail: 'Error' });
    vi.mocked(auth.session).mockRejectedValue(error);
    await expect(readEntrySession(auth)).rejects.toBe(error);
    expect(shouldEnterGuest(true, anonymous, error)).toBe(false);
  }
  vi.mocked(auth.session).mockRejectedValue(new Error('Network'));
  await expect(readEntrySession(auth)).rejects.toThrow('Network');
  expect(auth.guest).not.toHaveBeenCalled();
});

it('allows a deliberate MiniApp sign-in without the automatic-entry identity guard', async () => {
  const auth = repository();
  auth.miniApp = vi.fn().mockResolvedValue(guest);
  expect(await enterMiniAppOnce(auth, 'explicit-login-signature')).toBe(guest);
  expect(auth.miniApp).toHaveBeenCalledWith('explicit-login-signature');
});
it('reuses an existingguest or member session without another guestPOST', async () => {
  const auth = repository();
  for (const profile of [guest, { ...guest, isGuest: false, accountKind: 'member' as const }])
    expect(
      await enterGuestOnce(auth, { language: 'uz' }, { ...anonymous, authenticated: true, profile })
    ).toBe(profile);
  expect(auth.guest).not.toHaveBeenCalled();
});
it('deduplicates StrictMode double effects and allows retry only after a failed operation settles', async () => {
  const auth = repository();
  let resolve!: (profile: Profile) => void;
  vi.mocked(auth.guest).mockImplementationOnce(
    () =>
      new Promise<Profile>((finish) => {
        resolve = finish;
      })
  );
  const first = enterGuestOnce(auth, { language: 'uz' }, anonymous);
  const second = enterGuestOnce(auth, { language: 'uz' }, anonymous);
  expect(first).toBe(second);
  expect(auth.guest).toHaveBeenCalledTimes(1);
  resolve(guest);
  expect(await first).toBe(guest);
  vi.mocked(auth.guest).mockRejectedValueOnce(new Error('Failed'));
  await expect(enterGuestOnce(auth, { language: 'uz' }, anonymous)).rejects.toThrow('Failed');
  expect(await enterGuestOnce(auth, { language: 'uz' }, anonymous)).toBe(guest);
  expect(auth.guest).toHaveBeenCalledTimes(3);
});
it('preserves MiniApp login and deduplicates signatures without overwriting an authenticated account', async () => {
  const auth = repository();
  auth.miniApp = vi.fn().mockResolvedValue(guest);
  const first = enterMiniAppOnce(auth, 'signed-init-data', anonymous);
  const second = enterMiniAppOnce(auth, 'signed-init-data', anonymous);
  expect(first).toBe(second);
  expect(auth.miniApp).toHaveBeenCalledTimes(1);
  await first;
  const member = { ...guest, isGuest: false, accountKind: 'member' as const };
  expect(
    await enterMiniAppOnce(auth, 'another-init-data', {
      ...anonymous,
      authenticated: true,
      profile: member,
    })
  ).toBe(member);
  expect(auth.miniApp).toHaveBeenCalledTimes(1);
  expect(auth.guest).not.toHaveBeenCalled();
});
