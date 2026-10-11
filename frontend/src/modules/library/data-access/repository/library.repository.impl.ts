import type { LibraryRepository } from '../../domain';
import type {
  LibraryListDto,
  LibraryQuizDto,
  LibraryResultDto,
  LibraryDetailDto,
  LibraryPracticeDto,
} from '../dto';

import { apiClient } from 'src/shared/api';

import {
  mapLibraryList,
  mapLibraryQuiz,
  mapLibraryResult,
  mapLibraryDetail,
  mapLibraryPractice,
} from '../mappers';

export const libraryRepository: LibraryRepository = {
  list: async (params) => mapLibraryList(await apiClient.get<LibraryListDto>('library/', params)),
  detail: async (kind, id) =>
    mapLibraryDetail(await apiClient.get<LibraryDetailDto>(`library/${kind}/${id}/`)),
  favorite: (kind, id, saved) =>
    apiClient.post<{ saved: boolean }>(`library/${kind}/${id}/favorite/`, { saved }),
  study: async (kind, id) => {
    const result = await apiClient.post<{ created: boolean; is_studied: boolean }>(
      `library/${kind}/${id}/study/`
    );
    return { created: result.created, isStudied: result.is_studied };
  },
  practice: async (kind) =>
    mapLibraryPractice(await apiClient.get<LibraryPracticeDto>('library/practice/', { kind })),
  quiz: async (kind, extra, mode = 'text', itemId) =>
    mapLibraryQuiz(
      await apiClient.post<LibraryQuizDto>('library/quiz/', {
        kind,
        extra_practice: extra,
        mode,
        ...(itemId ? { item_id: itemId } : {}),
      })
    ),
  answer: async (id, option) =>
    mapLibraryResult(
      await apiClient.post<LibraryResultDto>(`library/quiz/${id}/answer/`, {
        selected_option: option,
      })
    ),
};
