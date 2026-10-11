import type { Profile, AuthSession, AuthRepository, GuestEntryInput } from '../domain';

import { ApiError } from 'src/shared/api';

/** Anonymous is a positive server response (or401), never inferred from403/server failures. */
export async function readEntrySession(repository: AuthRepository): Promise<AuthSession> {
  try {
    return await repository.session();
  } catch (error) {
    if (error instanceof ApiError && error.status === 401)
      return { authenticated: false, profile: null, botUsername: '' };
    throw error;
  }
}

/** Covers StrictMode double effects and simultaneous guest buttons without persisting identity. */
const pending = new WeakMap<AuthRepository, Promise<Profile>>();
const miniPending = new WeakMap<AuthRepository, Map<string, Promise<Profile>>>();
export function enterGuestOnce(
  repository: AuthRepository,
  input: GuestEntryInput,
  current?: AuthSession
): Promise<Profile> {
  if (current?.authenticated && current.profile) return Promise.resolve(current.profile);
  const active = pending.get(repository);
  if (active) return active;
  const operation = repository.guest(input).finally(() => {
    if (pending.get(repository) === operation) pending.delete(repository);
  });
  pending.set(repository, operation);
  return operation;
}
export const shouldEnterGuest = (
  autoGuest: boolean,
  session: AuthSession | undefined,
  error: unknown
) => autoGuest && Boolean(session && !session.authenticated) && !error;

/** Mini App signature stays only in the pending request, never in browser storage. */
export function enterMiniAppOnce(
  repository: AuthRepository,
  initData: string,
  current?: AuthSession
): Promise<Profile> {
  if (current?.authenticated && current.profile) return Promise.resolve(current.profile);
  const requests = miniPending.get(repository) ?? new Map<string, Promise<Profile>>();
  miniPending.set(repository, requests);
  const active = requests.get(initData);
  if (active) return active;
  const operation = repository.miniApp(initData).finally(() => {
    requests.delete(initData);
    if (!requests.size) miniPending.delete(repository);
  });
  requests.set(initData, operation);
  return operation;
}
