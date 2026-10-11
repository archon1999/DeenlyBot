import type { ArabicRepository } from '../../domain';
import type { ArabicQuizDto, LessonDetailDto, ArabicResultDto, ArabicOverviewDto } from '../dto';

import { apiClient } from 'src/shared/api';

import { mapArabicQuiz, mapLessonDetail, mapArabicResult, mapArabicOverview } from '../mappers';

export const arabicRepository: ArabicRepository = {
  overview: async () => mapArabicOverview(await apiClient.get<ArabicOverviewDto>('arabic/')),
  lesson: async (id) =>
    mapLessonDetail(await apiClient.get<LessonDetailDto>(`arabic/lessons/${id}/`)),
  start: (id) => apiClient.post<{ status: string }>(`arabic/lessons/${id}/start/`),
  complete: (id) => apiClient.post<{ status: string }>(`arabic/lessons/${id}/complete/`),
  quiz: async (extra, mode = 'text') =>
    mapArabicQuiz(
      await apiClient.post<ArabicQuizDto>('arabic/quiz/', { extra_practice: extra, mode })
    ),
  answer: async (id, option) =>
    mapArabicResult(
      await apiClient.post<ArabicResultDto>(`arabic/quiz/${id}/answer/`, {
        selected_option: option,
      })
    ),
};
