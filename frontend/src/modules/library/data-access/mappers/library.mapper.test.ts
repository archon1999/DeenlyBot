import { it, expect } from 'vitest';

import {
  mapLibraryQuiz,
  mapLibraryResult,
  mapLibraryDetail,
  mapLibraryPractice,
} from './library.mapper';

it('maps nullable questions and all four library question types without answer keys', () => {
  expect(mapLibraryQuiz({ question: null })).toBeNull();
  for (const quiz_type of [
    'arabic_meaning',
    'meaning_arabic',
    'arabic_title',
    'title_arabic',
  ] as const) {
    const question = mapLibraryQuiz({
      question: { id: 'q1', prompt: 'Prompt', quiz_type, options: [{ label: 'A' }] },
    });
    expect(question).toEqual({
      id: 'q1',
      prompt: 'Prompt',
      quizType: quiz_type,
      options: [{ label: 'A' }],
      audioTracks: [],
    });
  }
});
it('maps structured words, roots and verse analysis into a transport-independent detail', () => {
  const detail = mapLibraryDetail({
    id: 7,
    kind: 'surah',
    title: 'Ixlos',
    arabic_text: 'قُلْ',
    transcription: 'Qul',
    translation: 'Say',
    reference: '112',
    is_favorite: false,
    is_studied: true,
    audio_tracks: [],
    analysis: {
      summary: 'Summary',
      context: 'Context',
      explanation: 'Analysis',
      verses: [
        {
          key: '112:1',
          arabic_text: 'قُلْ',
          translation: 'Say',
          transcription: 'Qul',
          words: [
            {
              id: 5,
              arabic_text: 'قُلْ',
              root: 'ق و ل',
              meaning: 'Say',
              transcription: 'Qul',
              grammar_note: 'Imperative',
            },
          ],
        },
      ],
    },
  });
  expect(detail.analysis?.verses[0].words[0]).toEqual({
    id: '5',
    arabicText: 'قُلْ',
    root: 'ق و ل',
    meaning: 'Say',
    transcription: 'Qul',
    grammarNote: 'Imperative',
  });
  expect(detail.analysis?.verses[0]).not.toHaveProperty('arabic_text');
  expect(detail.isStudied).toBe(true);
});
it('maps server-owned stats and answer feedback', () => {
  expect(
    mapLibraryPractice({
      stats: { total_count: 11, studied_count: 4, due_count: 2, answers: 10, accuracy: 80 },
    })
  ).toEqual({
    totalCount: 11,
    studiedCount: 4,
    dueCount: 2,
    answers: 10,
    accuracy: 80,
    audioCount: 0,
  });
  expect(
    mapLibraryResult({
      accepted: false,
      is_correct: true,
      correct_option: 2,
      answer_label: 'Answer',
      answer_meaning: 'Meaning',
    })
  ).toEqual({
    accepted: false,
    isCorrect: true,
    correctOption: 2,
    answerLabel: 'Answer',
    answerMeaning: 'Meaning',
  });
});
