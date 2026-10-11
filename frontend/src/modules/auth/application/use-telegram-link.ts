import { useTelegramApproval } from './use-telegram-approval';
import { useStartTelegramLink, useCompleteTelegramLink } from './mutations';

export function useTelegramLinkFlow() {
  const start = useStartTelegramLink();
  const complete = useCompleteTelegramLink();
  return useTelegramApproval(
    {
      data: start.data,
      error: start.error,
      isPending: start.isPending,
      mutate: () => start.mutate(),
    },
    complete.mutateAsync
  );
}
