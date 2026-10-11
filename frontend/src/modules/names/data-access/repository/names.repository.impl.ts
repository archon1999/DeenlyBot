import type { NamesRepository } from '../../domain';
import type { NamesDto, NameQuizDto, NameResultDto } from '../dto';

import { apiClient } from 'src/shared/api';

import { mapQuiz, mapNames, mapResult } from '../mappers';

export const namesRepository: NamesRepository = {
  overview: async () => mapNames(await apiClient.get<NamesDto>('names/')),
  confirm: (id) => apiClient.post<{ created: boolean }>(`names/${id}/confirm/`),
  quiz: async (extraPractice) =>
    mapQuiz(await apiClient.post<NameQuizDto>('names/quiz/', { extra_practice: extraPractice })),
  answer: async (id, option) =>
    mapResult(
      await apiClient.post<NameResultDto>(`names/quiz/${id}/answer/`, { selected_option: option })
    ),
};
