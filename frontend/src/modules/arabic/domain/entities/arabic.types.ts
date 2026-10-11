import type { AudioTrack } from 'src/shared/domain/audio';

export type ArabicCategory =
  | 'alphabet'
  | 'quran_vocabulary'
  | 'grammar'
  | 'prayer_arabic'
  | 'sarf'
  | 'daily_phrases'
  | 'listening';
export type ArabicCategoryInfo = { key: ArabicCategory; title: string; description: string };
export type ArabicQuizType =
  | 'arabic_meaning'
  | 'meaning_arabic'
  | 'arabic_transcription'
  | 'transcription_arabic'
  | 'missing_word'
  | 'audio_arabic'
  | 'audio_meaning';
export type ArabicLesson = {
  id: number;
  slug: string;
  category: ArabicCategory;
  order: number;
  title: string;
  summary: string;
  previewArabic: string[];
  estimatedMinutes: number;
  status: 'new' | 'in_progress' | 'completed';
};
export type ArabicItem = {
  id: number;
  arabicText: string;
  transcription: string;
  meaning: string;
  explanation: string;
  itemType: string;
  audioTracks?: AudioTrack[];
  quranReference?: string;
  quranPassage?: { id: number; kind: 'ayah' | 'surah' };
};
export type ArabicLessonDetail = ArabicLesson & { explanation: string; items: ArabicItem[] };
export type ArabicStats = {
  completedLessons: number;
  totalLessons: number;
  introducedItems: number;
  dueItems: number;
  answers: number;
  accuracy: number;
  audioCount?: number;
};
export type ArabicOverview = {
  lessons: ArabicLesson[];
  stats: ArabicStats;
  categories: ArabicCategoryInfo[];
};
export type ArabicQuestion = {
  id: string;
  prompt: string;
  quizType: ArabicQuizType;
  options: { label: string }[];
  audioTracks?: AudioTrack[];
};
export type ArabicQuizResult = {
  accepted: boolean;
  isCorrect: boolean;
  correctOption: number;
  answerLabel: string;
  answerMeaning: string;
};
