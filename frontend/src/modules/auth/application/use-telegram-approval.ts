import type { LoginChallenge, LoginCompletion } from '../domain';

import { useState, useEffect } from 'react';

type StartState = {
  data: LoginChallenge | undefined;
  error: unknown;
  isPending: boolean;
  mutate: () => void;
};
export function useTelegramApproval(start: StartState, complete: () => Promise<LoginCompletion>) {
  const [expired, setExpired] = useState(false);
  const [approved, setApproved] = useState(false);
  const [pollError, setPollError] = useState<unknown>(null);
  useEffect(() => {
    const challenge = start.data;
    if (!challenge) return undefined;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      if (stopped) return;
      if (Date.now() >= new Date(challenge.expiresAt).getTime()) {
        setExpired(true);
        return;
      }
      try {
        const result = await complete();
        if (stopped) return;
        if (result.status === 'approved') {
          setApproved(true);
          return;
        }
        timer = setTimeout(poll, 2000);
      } catch (error) {
        if (!stopped) setPollError(error);
      }
    };
    timer = setTimeout(poll, 1500);
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [start.data, complete]);
  return {
    challenge: start.data,
    expired,
    approved,
    error: pollError ?? start.error,
    isStarting: start.isPending,
    waiting: Boolean(start.data && !expired && !pollError && !approved),
    startApproval: () => {
      setExpired(false);
      setApproved(false);
      setPollError(null);
      start.mutate();
    },
  };
}
