import type {
  LessonDto,
  ArabicQuizDto,
  LessonDetailDto,
  ArabicResultDto,
  ArabicOverviewDto,
} from '../dto';
import type {
  ArabicLesson,
  ArabicOverview,
  ArabicQuestion,
  ArabicQuizResult,
  ArabicLessonDetail,
} from '../../domain';

import { mapAudioTracks } from 'src/shared/audio/audio.dto';
import { mapContentProvenance } from 'src/shared/api/content-provenance';

export const mapLesson = (d: LessonDto): ArabicLesson => ({
  id: d.id,
  slug: d.slug,
  category: d.category,
  order: d.order,
  title: d.title,
  summary: d.summary,
  previewArabic: [...(d.preview_arabic ?? [])],
  estimatedMinutes: d.estimated_minutes,
  status: d.status,
});
export const mapLessonDetail = (d: LessonDetailDto): ArabicLessonDetail => ({
  ...mapLesson(d),
  provenance: mapContentProvenance(d.provenance),
  explanation: d.explanation,
  items: d.items.map((item) => ({
    id: item.id,
    arabicText: item.arabic_text,
    transcription: item.transcription,
    meaning: item.meaning,
    explanation: item.explanation,
    itemType: item.item_type,
    audioTracks: mapAudioTracks(item.audio_tracks),
    quranReference: item.quran_reference,
    quranPassage: item.quran_passage ? { ...item.quran_passage } : undefined,
  })),
});
export const mapArabicOverview = (d: ArabicOverviewDto): ArabicOverview => ({
  lessons: d.lessons.map(mapLesson),
  categories: (d.categories ?? []).map((category) => ({ ...category })),
  stats: {
    completedLessons: d.stats.completed_lessons,
    totalLessons: d.stats.total_lessons,
    introducedItems: d.stats.introduced_items,
    dueItems: d.stats.due_items,
    answers: d.stats.answers,
    accuracy: d.stats.accuracy,
    audioCount: d.stats.audio_count ?? 0,
  },
});
export const mapArabicQuiz = (d: ArabicQuizDto): ArabicQuestion | null =>
  d.question
    ? {
        id: d.question.id,
        prompt: d.question.prompt,
        quizType: d.question.quiz_type,
        options: d.question.options,
        audioTracks: mapAudioTracks(d.question.audio_tracks),
      }
    : null;
export const mapArabicResult = (d: ArabicResultDto): ArabicQuizResult => ({
  accepted: d.accepted,
  isCorrect: d.is_correct,
  correctOption: d.correct_option,
  answerLabel: d.answer_label,
  answerMeaning: d.answer_meaning,
});
