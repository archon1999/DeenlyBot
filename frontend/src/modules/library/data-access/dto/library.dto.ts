import type { AudioTrackDto } from 'src/shared/audio/audio.dto';
import type { ContentProvenanceDto } from 'src/shared/api/content-provenance';

export type LibraryItemDto = {
  provenance?: ContentProvenanceDto;
  id: number;
  kind: 'ayah' | 'surah' | 'dua';
  title: string;
  arabic_text: string;
  transcription: string;
  translation: string;
  reference: string;
  is_favorite: boolean;
  is_studied: boolean;
  audio_tracks?: AudioTrackDto[];
};
export type LibraryDetailDto = LibraryItemDto & {
  analysis: {
    provenance?: ContentProvenanceDto;
    summary: string;
    context: string;
    explanation: string;
    verses: {
      key: string;
      arabic_text: string;
      translation: string;
      transcription: string;
      words: {
        id: string | number;
        arabic_text: string;
        root: string;
        meaning: string;
        transcription: string;
        grammar_note: string;
      }[];
    }[];
  } | null;
};
export type LibraryPracticeDto = {
  stats: {
    total_count: number;
    studied_count: number;
    due_count: number;
    answers: number;
    accuracy: number;
    audio_count?: number;
  };
};
export type LibraryQuizDto = {
  question: {
    id: string;
    prompt: string;
    quiz_type:
      | 'arabic_meaning'
      | 'meaning_arabic'
      | 'arabic_title'
      | 'title_arabic'
      | 'audio_arabic'
      | 'audio_meaning';
    options: { label: string }[];
    audio_tracks?: AudioTrackDto[];
  } | null;
};
export type LibraryResultDto = {
  accepted: boolean;
  is_correct: boolean;
  correct_option: number;
  answer_label: string;
  answer_meaning: string;
};
export type LibraryListDto = {
  results: LibraryItemDto[];
  count: number;
  page: number;
  pages: number;
};
