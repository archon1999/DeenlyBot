import type { PracticeMode } from 'src/shared/domain/audio';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { arabicKeys } from './keys';
import { arabicRepository } from '../data-access';

const useInvalidateArabic = () => {
  const client = useQueryClient();
  return async () => {
    await Promise.all(
      [arabicKeys.all, ['dashboard'], ['reports']].map((key) =>
        client.invalidateQueries({ queryKey: key })
      )
    );
  };
};
export const useStartArabicLesson = () => {
  const invalidate = useInvalidateArabic();
  return useMutation({
    mutationFn: (id: number) => arabicRepository.start(id),
    onSuccess: invalidate,
  });
};
export const useCompleteArabicLesson = () => {
  const invalidate = useInvalidateArabic();
  return useMutation({
    mutationFn: (id: number) => arabicRepository.complete(id),
    onSuccess: invalidate,
  });
};
export const useArabicQuiz = () =>
  useMutation({
    mutationFn: ({ extra, mode }: { extra: boolean; mode: PracticeMode }) =>
      arabicRepository.quiz(extra, mode),
  });
export const useAnswerArabicQuiz = () => {
  const invalidate = useInvalidateArabic();
  return useMutation({
    mutationFn: ({ id, option }: { id: string; option: number }) =>
      arabicRepository.answer(id, option),
    onSuccess: invalidate,
  });
};
