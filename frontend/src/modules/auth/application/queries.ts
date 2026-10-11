import { useQuery, useQueryClient } from '@tanstack/react-query';

import { authKeys } from './keys';
import { authRepository } from '../data-access';
import { readEntrySession } from './guest-session';
import { reconcileSessionIdentity } from './session-cache';

export function useSessionQuery() {
  const client = useQueryClient();
  return useQuery({
    queryKey: authKeys.session,
    queryFn: async ({ signal }) => {
      const session = await readEntrySession(authRepository);
      if (!signal.aborted) await reconcileSessionIdentity(client, session);
      return session;
    },
    staleTime: 60_000,
  });
}
export function useProfileQuery(enabled = true) {
  return useQuery({ queryKey: authKeys.profile, queryFn: authRepository.profile, enabled });
}
