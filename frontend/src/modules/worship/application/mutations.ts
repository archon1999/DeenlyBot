import type { QadaAdd, FastAction, FastIntent, QadaSummary, QadaConfigure } from '../domain';

import { useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { worshipKeys } from './keys';
import { prepareFastOperation } from '../domain';
import { worshipRepository } from '../data-access';

const useQadaUpdated = () => {
  const client = useQueryClient();
  return async (data: QadaSummary) => {
    client.setQueryData(worshipKeys.all, data);
    await Promise.all(
      [worshipKeys.all, ['dashboard'], ['reports']].map((key) =>
        client.invalidateQueries({ queryKey: key })
      )
    );
  };
};
export const useConfigureQada = () => {
  const update = useQadaUpdated();
  return useMutation({
    mutationFn: (p: QadaConfigure) => worshipRepository.configure(p),
    onSuccess: update,
  });
};
export const useAddQada = () => {
  const update = useQadaUpdated();
  return useMutation({ mutationFn: (p: QadaAdd) => worshipRepository.add(p), onSuccess: update });
};
export const useCompleteQada = () => {
  const update = useQadaUpdated();
  return useMutation({
    mutationFn: (key: string) => worshipRepository.complete(key),
    onSuccess: update,
  });
};
export const useFastAction = () => {
  const update = useQadaUpdated();
  const operation = useRef<FastAction | null>(null);
  return useMutation({
    mutationFn: (intent: FastIntent) => {
      operation.current = prepareFastOperation(operation.current, intent, () =>
        crypto.randomUUID()
      );
      return worshipRepository.fast(operation.current);
    },
    onSuccess: async (data) => {
      operation.current = null;
      await update(data);
    },
  });
};
