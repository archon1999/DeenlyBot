import { useMutation, useQueryClient } from '@tanstack/react-query';

import { namesKeys } from './keys';
import { namesRepository } from '../data-access';

export const useConfirmName = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => namesRepository.confirm(id),
    onSuccess: async () => {
      await Promise.all(
        [namesKeys.all, ['dashboard'], ['reports']].map((key) =>
          client.invalidateQueries({ queryKey: key })
        )
      );
    },
  });
};
export const useNameQuiz = () =>
  useMutation({ mutationFn: (extraPractice: boolean) => namesRepository.quiz(extraPractice) });
export const useAnswerNameQuiz = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, option }: { id: string; option: number }) =>
      namesRepository.answer(id, option),
    onSuccess: async () => {
      await Promise.all(
        [namesKeys.all, ['dashboard'], ['reports']].map((key) =>
          client.invalidateQueries({ queryKey: key })
        )
      );
    },
  });
};
