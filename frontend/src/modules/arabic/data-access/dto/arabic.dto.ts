import type { AudioTrackDto } from 'src/shared/audio/audio.dto';

export type ArabicCategoryDto =
  | 'alphabet'
  | 'quran_vocabulary'
  | 'grammar'
  | 'prayer_arabic'
  | 'sarf'
  | 'daily_phrases'
  | 'listening';
export type LessonDto = {
  id: number;
  slug: string;
  category: ArabicCategoryDto;
  order: number;
  title: string;
  summary: string;
  preview_arabic?: string[];
  estimated_minutes: number;
  status: 'new' | 'in_progress' | 'completed';
};
export type LessonDetailDto = LessonDto & {
  explanation: string;
  items: {
    id: number;
    arabic_text: string;
    transcription: string;
    meaning: string;
    explanation: string;
    item_type: string;
    audio_tracks?: AudioTrackDto[];
    quran_reference?: string;
    quran_passage?: { id: number; kind: 'ayah' | 'surah' } | null;
  }[];
};
export type ArabicOverviewDto = {
  lessons: LessonDto[];
  categories?: { key: ArabicCategoryDto; title: string; description: string }[];
  stats: {
    completed_lessons: number;
    total_lessons: number;
    introduced_items: number;
    due_items: number;
    answers: number;
    accuracy: number;
    audio_count?: number;
  };
};
export type ArabicQuizDto = {
  question: {
    id: string;
    prompt: string;
    quiz_type:
      | 'arabic_meaning'
      | 'meaning_arabic'
      | 'arabic_transcription'
      | 'transcription_arabic'
      | 'missing_word'
      | 'audio_arabic'
      | 'audio_meaning';
    options: { label: string }[];
    audio_tracks?: AudioTrackDto[];
  } | null;
};
export type ArabicResultDto = {
  accepted: boolean;
  is_correct: boolean;
  correct_option: number;
  answer_label: string;
  answer_meaning: string;
};
