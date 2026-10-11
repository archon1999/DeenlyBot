import type { Query, QueryClient } from '@tanstack/react-query';
import type { Profile, AuthSession } from '../domain';

import { authKeys } from './keys';

const isPersonalQuery = (query: Query) =>
  !(query.queryKey[0] === 'auth' && query.queryKey[1] === 'session');

export async function clearPersonalQueries(client: QueryClient) {
  await client.cancelQueries({ predicate: isPersonalQuery });
  client.removeQueries({ predicate: isPersonalQuery });
}
export async function reconcileSessionIdentity(client: QueryClient, session: AuthSession) {
  const previous = client.getQueryData<AuthSession>(authKeys.session);
  if (previous && previous.profile?.id !== session.profile?.id) await clearPersonalQueries(client);
}
export async function applyAuthenticatedProfile(client: QueryClient, profile: Profile) {
  await client.cancelQueries();
  const previous = client.getQueryData<AuthSession>(authKeys.session);
  if (previous?.profile?.id !== profile.id) await clearPersonalQueries(client);
  client.setQueryData<AuthSession>(authKeys.session, {
    authenticated: true,
    profile,
    botUsername: previous?.botUsername ?? '',
  });
  client.setQueryData(authKeys.profile, profile);
  await client.invalidateQueries();
}
export async function applySignedOutSession(client: QueryClient) {
  const previous = client.getQueryData<AuthSession>(authKeys.session);
  await client.cancelQueries();
  await clearPersonalQueries(client);
  client.setQueryData<AuthSession>(authKeys.session, {
    authenticated: false,
    profile: null,
    botUsername: previous?.botUsername ?? '',
  });
  await client.invalidateQueries({ queryKey: authKeys.session });
}
