import { useRef, useEffect } from 'react';

import { useTelegramApproval } from './use-telegram-approval';
import { useStartLogin, useMiniAppLogin, useCompleteLogin } from './mutations';

export function useTelegramLoginFlow() {
  const start = useStartLogin();
  const complete = useCompleteLogin();
  const miniApp = useMiniAppLogin();
  const miniAttempted = useRef(false);
  const miniData = window.Telegram?.WebApp?.initData;
  const miniMutate = miniApp.mutate;
  useEffect(() => {
    if (miniData && !miniAttempted.current) {
      miniAttempted.current = true;
      miniMutate(miniData);
      window.Telegram?.WebApp?.ready?.();
    }
  }, [miniData, miniMutate]);
  const flow = useTelegramApproval(
    {
      data: start.data,
      error: start.error,
      isPending: start.isPending,
      mutate: () => start.mutate(),
    },
    complete.mutateAsync
  );
  return {
    ...flow,
    error: flow.error ?? miniApp.error,
    isMiniAppPending: miniApp.isPending,
    isMiniAppApproved: miniApp.isSuccess,
    startLogin: flow.startApproval,
  };
}
