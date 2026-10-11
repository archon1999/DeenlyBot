import { it, vi, expect } from 'vitest';

import { apiClient } from 'src/shared/api';

import { arabicRepository } from './arabic.repository.impl';

vi.mock('src/shared/api', () => ({ apiClient: { get: vi.fn(), post: vi.fn() } }));
it('requests text or listening practice explicitly while leaving study commands separate', async () => {
  vi.mocked(apiClient.post).mockResolvedValue({ question: null });
  await arabicRepository.quiz(true, 'listening');
  expect(apiClient.post).toHaveBeenCalledWith('arabic/quiz/', {
    extra_practice: true,
    mode: 'listening',
  });
  await arabicRepository.quiz(false);
  expect(apiClient.post).toHaveBeenCalledWith('arabic/quiz/', {
    extra_practice: false,
    mode: 'text',
  });
});
