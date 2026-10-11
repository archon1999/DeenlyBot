import type { LibraryKind, LibraryParams, LibraryFilter } from '../domain';

import { useQuery } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { libraryKeys } from './keys';
import { libraryRepository } from '../data-access';
import { sameLibraryScope } from './library-query-scope';

export const useLibrary = (params: LibraryParams) => {
  const { language } = useLocale();
  return useQuery({
    queryKey: libraryKeys.list(language, params),
    queryFn: () => libraryRepository.list(params),
    placeholderData: (previousData, previousQuery) =>
      sameLibraryScope(
        previousQuery?.queryKey[2],
        previousQuery?.queryKey[3] as LibraryParams | undefined,
        language,
        params
      )
        ? previousData
        : undefined,
  });
};

export const useLibraryPractice = (kind: LibraryFilter) => {
  const { language } = useLocale();
  return useQuery({
    queryKey: libraryKeys.practice(language, kind),
    queryFn: () => libraryRepository.practice(kind),
  });
};

export const useLibraryDetail = (kind: LibraryKind, id: number | null) => {
  const { language } = useLocale();
  return useQuery({
    queryKey: libraryKeys.detail(language, kind, id),
    queryFn: () => libraryRepository.detail(kind, id!),
    enabled: id !== null,
  });
};
