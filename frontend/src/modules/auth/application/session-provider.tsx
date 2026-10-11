import type { AuthSession } from '../domain';

import { useEffect, useContext, createContext } from 'react';

import { useLocale } from 'src/shared/i18n';

import { useSessionQuery } from './queries';
import { shouldEnterGuest } from './guest-session';
import { useLogout, useGuestEntry, useMiniAppLogin } from './mutations';

type SessionValue = AuthSession & {
  isLoading: boolean;
  error: unknown;
  refreshSession: () => Promise<unknown>;
  logout: () => Promise<void>;
};
const SessionContext = createContext<SessionValue | null>(null);
export function SessionProvider({
  children,
  autoGuest = true,
}: {
  children: React.ReactNode;
  autoGuest?: boolean;
}) {
  const session = useSessionQuery();
  const logout = useLogout();
  const guest = useGuestEntry();
  const mini = useMiniAppLogin(true);
  const miniData = typeof window === 'undefined' ? undefined : window.Telegram?.WebApp?.initData;
  const miniEntry = Boolean(autoGuest && miniData && !mini.isSuccess);
  const { language, setLanguage } = useLocale();
  const guestMutate = guest.mutate;
  const guestReset = guest.reset;
  const miniMutate = mini.mutate;
  const miniReset = mini.reset;
  useEffect(() => {
    if (session.data?.authenticated && !mini.isPending && mini.error) miniReset();
  }, [session.data?.authenticated, mini.isPending, mini.error, miniReset]);
  useEffect(() => {
    if (
      miniEntry &&
      miniData &&
      session.data &&
      !session.data.authenticated &&
      !session.error &&
      !mini.isPending &&
      !mini.isSuccess &&
      !mini.error
    )
      miniMutate(miniData);
  }, [
    miniEntry,
    miniData,
    session.data,
    session.error,
    mini.isPending,
    mini.isSuccess,
    mini.error,
    miniMutate,
  ]);
  useEffect(() => {
    if (
      !miniEntry &&
      shouldEnterGuest(autoGuest, session.data, session.error) &&
      !guest.isPending &&
      !guest.isSuccess &&
      !guest.error
    )
      guestMutate({ language });
  }, [
    autoGuest,
    miniEntry,
    session.data,
    session.error,
    guest.isPending,
    guest.isSuccess,
    guest.error,
    guestMutate,
    language,
  ]);
  useEffect(() => {
    if (session.data?.authenticated && !guest.isPending) guestReset();
  }, [session.data?.authenticated, guest.isPending, guestReset]);
  const profileLanguage = session.data?.profile?.language;
  useEffect(() => {
    if (profileLanguage) setLanguage(profileLanguage);
  }, [profileLanguage, setLanguage]);
  return (
    <SessionContext.Provider
      value={{
        authenticated: session.data?.authenticated ?? false,
        profile: session.data?.profile ?? null,
        botUsername: session.data?.botUsername ?? '',
        isLoading:
          session.isPending ||
          (autoGuest &&
            !session.data?.authenticated &&
            !session.error &&
            !guest.error &&
            !mini.error),
        error: session.error || (autoGuest ? mini.error || guest.error : null),
        refreshSession: () => {
          guest.reset();
          mini.reset();
          return session.refetch();
        },
        logout: () => logout.mutateAsync(),
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}
export function useSession() {
  const session = useContext(SessionContext);
  if (!session) throw new Error('SessionProvider is missing');
  return session;
}
