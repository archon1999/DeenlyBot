import { it, expect, describe } from 'vitest';

import { mapLesson, mapArabicQuiz, mapLessonDetail, mapArabicOverview } from './arabic.mapper';

describe('Arabic learning transport boundary', () => {
  it('keeps the actual lesson-specific Arabic preview instead of a repeated category title', () => {
    const dto = {
      id: 2,
      slug: 'ta-tha',
      category: 'alphabet' as const,
      order: 2,
      title: 'Ta va Tha',
      summary: 'Ikkinchi dars',
      estimated_minutes: 6,
      status: 'new' as const,
      preview_arabic: ['ت', 'ث'],
    };
    const lesson = mapLesson(dto);
    expect(lesson.previewArabic).toEqual(['ت', 'ث']);
    expect(lesson.previewArabic).not.toBe(dto.preview_arabic);
    expect(lesson).not.toHaveProperty('preview_arabic');
  });
  it('turns the service counters into a transport-independent domain object', () => {
    const overview = mapArabicOverview({
      lessons: [],
      stats: {
        completed_lessons: 3,
        total_lessons: 38,
        introduced_items: 9,
        due_items: 2,
        answers: 10,
        accuracy: 80,
      },
    });
    expect(overview.stats.completedLessons).toBe(3);
    expect(overview.stats.totalLessons).toBe(38);
    expect(overview.stats.introducedItems).toBe(9);
    expect(overview.stats.dueItems).toBe(2);
    expect(overview.stats).not.toHaveProperty('completed_lessons');
  });
  it('uses categories from the server and maps listening tracks without revealing answer keys', () => {
    const overview = mapArabicOverview({
      categories: [
        { key: 'prayer_arabic', title: 'Namoz arabchasi', description: 'Namoz matnlari' },
        { key: 'sarf', title: 'Sarf', description: 'So‘z yasalishi' },
      ],
      lessons: [],
      stats: {
        completed_lessons: 4,
        total_lessons: 50,
        introduced_items: 12,
        due_items: 2,
        answers: 10,
        accuracy: 80,
        audio_count: 5,
      },
    });
    expect(overview.categories.map((category) => category.key)).toEqual(['prayer_arabic', 'sarf']);
    expect(overview.stats.audioCount).toBe(5);
    const question = mapArabicQuiz({
      question: {
        id: 'q',
        prompt: 'Listen',
        quiz_type: 'audio_arabic',
        options: [{ label: 'أ' }],
        audio_tracks: [{ id: 'clip', label: 'Audio', voice: '', url: '/media/1.mp3' }],
      },
    });
    expect(question?.audioTracks?.[0].id).toBe('clip');
    expect(question).not.toHaveProperty('correct_option');
  });
  it('maps item audio and Quran reference while preserving original lesson identity', () => {
    const lesson = mapLessonDetail({
      id: 3,
      slug: 'lesson3',
      category: 'prayer_arabic',
      order: 1,
      title: 'Takbir',
      summary: 'Takbir',
      estimated_minutes: 6,
      status: 'new',
      explanation: 'Read',
      items: [
        {
          id: 8,
          arabic_text: 'اللَّهُ',
          transcription: 'Alloh',
          meaning: 'Alloh',
          explanation: 'Meaning',
          item_type: 'word',
          quran_reference: '1:1',
          quran_passage: { id: 7, kind: 'surah' },
          audio_tracks: [{ id: 'a', label: 'Audio', voice: '', url: '/media/1.mp3' }],
        },
      ],
    });
    expect(lesson.id).toBe(3);
    expect(lesson.items[0].audioTracks?.[0].url).toBe('/media/1.mp3');
    expect(lesson.items[0].quranReference).toBe('1:1');
    expect(lesson.items[0].quranPassage).toEqual({ id: 7, kind: 'surah' });
  });
});
