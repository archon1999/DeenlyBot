import type { Profile, AuthSession } from '../domain';

import { it, expect, describe } from 'vitest';
import { QueryClient } from '@tanstack/react-query';

import { authKeys } from './keys';
import {
  applySignedOutSession,
  reconcileSessionIdentity,
  applyAuthenticatedProfile,
} from './session-cache';

const guest: Profile = {
  id: 1,
  firstName: '',
  username: '',
  language: 'uz',
  timezone: 'Asia/Tashkent',
  accountKind: 'guest',
  isGuest: true,
  email: '',
  telegramLinked: false,
};
function seededClient() {
  const client = new QueryClient();
  client.setQueryData<AuthSession>(authKeys.session, {
    authenticated: true,
    profile: guest,
    botUsername: 'deenly_bot',
  });
  client.setQueryData(['dashboard', 'uz'], { namesIntroduced: 4 });
  client.setQueryData(authKeys.profile, guest);
  return client;
}
describe('account session cache isolation', () => {
  it('retains same-profile guest progress when the server upgrades the identity', async () => {
    const client = seededClient();
    const member = {
      ...guest,
      accountKind: 'member' as const,
      isGuest: false,
      email: 'laylo@example.com',
    };
    await applyAuthenticatedProfile(client, member);
    expect(client.getQueryData(['dashboard', 'uz'])).toEqual({ namesIntroduced: 4 });
    expect(client.getQueryData<Profile>(authKeys.profile)?.isGuest).toBe(false);
  });
  it('clears every previous personal profile cache before another account becomes visible', async () => {
    const client = seededClient();
    const other = {
      ...guest,
      id: 2,
      accountKind: 'member' as const,
      isGuest: false,
      email: 'other@example.com',
    };
    await applyAuthenticatedProfile(client, other);
    expect(client.getQueryData(['dashboard', 'uz'])).toBeUndefined();
    expect(client.getQueryData<Profile>(authKeys.profile)?.id).toBe(2);
    expect(client.getQueryData<AuthSession>(authKeys.session)?.profile?.id).toBe(2);
  });
  it('clears personal data when a refreshed server session reveals another identity', async () => {
    const client = seededClient();
    await reconcileSessionIdentity(client, {
      authenticated: true,
      profile: { ...guest, id: 3 },
      botUsername: 'deenly_bot',
    });
    expect(client.getQueryData(['dashboard', 'uz'])).toBeUndefined();
    expect(client.getQueryData(authKeys.profile)).toBeUndefined();
  });
  it('signs out without leaving an auth/profile cache available to the next guest', async () => {
    const client = seededClient();
    await applySignedOutSession(client);
    expect(client.getQueryData(authKeys.profile)).toBeUndefined();
    expect(client.getQueryData(['dashboard', 'uz'])).toBeUndefined();
    expect(client.getQueryData<AuthSession>(authKeys.session)?.authenticated).toBe(false);
  });
});
