import { it, vi, expect, describe, beforeEach } from 'vitest';

import { apiClient } from 'src/shared/api';

import { libraryRepository } from './library.repository.impl';

vi.mock('src/shared/api', () => ({ apiClient: { get: vi.fn(), post: vi.fn() } }));
describe('library commands', () => {
  beforeEach(() => vi.clearAllMocks());
  it('sets the requested favorite state on retry rather than toggling it', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ saved: false });
    await libraryRepository.favorite('dua', 12, false);
    await libraryRepository.favorite('dua', 12, false);
    expect(apiClient.post).toHaveBeenNthCalledWith(1, 'library/dua/12/favorite/', { saved: false });
    expect(apiClient.post).toHaveBeenNthCalledWith(2, 'library/dua/12/favorite/', { saved: false });
  });
  it('sends language-independent pagination and query to the backend', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ results: [], count: 11, page: 2, pages: 2 });
    const result = await libraryRepository.list({ kind: 'ayah', page: 2, q: 'Yunus' });
    expect(apiClient.get).toHaveBeenCalledWith('library/', { kind: 'ayah', page: 2, q: 'Yunus' });
    expect(result.page).toBe(2);
    expect(result.pages).toBe(2);
  });
  it('introduces content explicitly and scopes practice to the selected collection', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ created: true, is_studied: true });
    expect(await libraryRepository.study('surah', 7)).toEqual({ created: true, isStudied: true });
    expect(apiClient.post).toHaveBeenCalledWith('library/surah/7/study/');
    vi.mocked(apiClient.get).mockResolvedValue({
      stats: { studied_count: 4, due_count: 1, answers: 2, accuracy: 50 },
    });
    expect((await libraryRepository.practice('favorites')).studiedCount).toBe(4);
    expect(apiClient.get).toHaveBeenCalledWith('library/practice/', { kind: 'favorites' });
  });
  it('creates extra practice and submits the chosen option with the question UUID', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ question: null });
    expect(await libraryRepository.quiz('dua', true)).toBeNull();
    expect(apiClient.post).toHaveBeenCalledWith('library/quiz/', {
      kind: 'dua',
      extra_practice: true,
      mode: 'text',
    });
    vi.mocked(apiClient.post).mockResolvedValue({
      accepted: true,
      is_correct: false,
      correct_option: 1,
      answer_label: 'A',
      answer_meaning: 'M',
    });
    expect((await libraryRepository.answer('uuid', 2)).correctOption).toBe(1);
    expect(apiClient.post).toHaveBeenCalledWith('library/quiz/uuid/answer/', {
      selected_option: 2,
    });
  });
  it('loads structured detail by kind and ID, and submits targeted listening without changing study state', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      id: 7,
      kind: 'surah',
      title: 'Ikhlas',
      arabic_text: 'قُلْ',
      transcription: 'Qul',
      translation: 'Say',
      reference: '112',
      is_favorite: false,
      is_studied: true,
      analysis: null,
      audio_tracks: [],
    });
    expect((await libraryRepository.detail('surah', 7)).analysis).toBeNull();
    expect(apiClient.get).toHaveBeenCalledWith('library/surah/7/');
    vi.mocked(apiClient.post).mockResolvedValue({ question: null });
    await libraryRepository.quiz('surah', true, 'listening', 7);
    expect(apiClient.post).toHaveBeenCalledWith('library/quiz/', {
      kind: 'surah',
      extra_practice: true,
      mode: 'listening',
      item_id: 7,
    });
    expect(apiClient.post).toHaveBeenCalledTimes(1);
  });
});
