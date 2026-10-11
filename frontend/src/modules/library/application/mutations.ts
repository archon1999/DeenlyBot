import type { LibraryKind, LibraryFilter } from '../domain';
import type { PracticeMode } from 'src/shared/domain/audio';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { libraryKeys } from './keys';
import { libraryRepository } from '../data-access';

export const useSaveFavorite = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ kind, id, saved }: { kind: LibraryKind; id: number; saved: boolean }) =>
      libraryRepository.favorite(kind, id, saved),
    onSuccess: () => client.invalidateQueries({ queryKey: libraryKeys.all }),
  });
};

export const useStudyLibraryItem = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ kind, id }: { kind: LibraryKind; id: number }) =>
      libraryRepository.study(kind, id),
    onSuccess: () => client.invalidateQueries({ queryKey: libraryKeys.all }),
  });
};
export const useLibraryQuiz = (kind: LibraryFilter, itemId?: number) =>
  useMutation({
    mutationFn: ({ extra, mode }: { extra: boolean; mode: PracticeMode }) =>
      libraryRepository.quiz(kind, extra, mode, itemId),
  });
export const useAnswerLibraryQuiz = () => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, option }: { id: string; option: number }) =>
      libraryRepository.answer(id, option),
    onSuccess: () => client.invalidateQueries({ queryKey: libraryKeys.all }),
  });
};
