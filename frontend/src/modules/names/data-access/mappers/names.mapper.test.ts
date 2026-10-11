import { it, expect, describe } from 'vitest';

import { mapQuiz, mapNames, mapResult } from './names.mapper';

describe('name learning transport boundary', () => {
  it('keeps the existing dataset numbering and sequential next identity', () => {
    const result = mapNames({
      results: [
        {
          id: 407,
          order: 100,
          arabic: 'الصبور',
          transcription: 'As-Sabur',
          meaning: 'Patient',
          description: 'Meaning',
          status: 'new',
          is_next: true,
        },
      ],
      total: 100,
      introduced_count: 99,
      learned_count: 41,
      due_count: 3,
      next_id: 407,
    });
    expect(result.total).toBe(100);
    expect(result.results[0].order).toBe(100);
    expect(result.nextId).toBe(407);
    expect(result.results[0].isNext).toBe(true);
  });
  it('keeps locked review and answered quiz results distinct', () => {
    expect(mapQuiz({ question: null, required_names: 4 })).toEqual({
      question: null,
      requiredNames: 4,
    });
    const result = mapResult({
      accepted: false,
      is_correct: true,
      correct_option: 3,
      answer_label: 'Al-Wadud',
      answer_meaning: 'Loving',
    });
    expect(result.accepted).toBe(false);
    expect(result.isCorrect).toBe(true);
    expect(result.correctOption).toBe(3);
  });
});
