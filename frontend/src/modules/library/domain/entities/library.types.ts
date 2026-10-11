import type { AudioTrack } from 'src/shared/domain/audio';

export type LibraryKind = 'ayah' | 'surah' | 'dua';
export type LibraryFilter = LibraryKind | 'favorites';
export type LibraryItem = {
  id: number;
  kind: LibraryKind;
  title: string;
  arabicText: string;
  transcription: string;
  translation: string;
  reference: string;
  isFavorite: boolean;
  isStudied: boolean;
  audioTracks?: AudioTrack[];
};
export type LibraryWord = {
  id: string;
  arabicText: string;
  root: string;
  meaning: string;
  transcription: string;
  grammarNote: string;
};
export type LibraryAnalysis = {
  summary: string;
  context: string;
  explanation: string;
  verses: {
    key: string;
    arabicText: string;
    translation: string;
    transcription: string;
    words: LibraryWord[];
  }[];
};
export type LibraryDetail = LibraryItem & { analysis: LibraryAnalysis | null };
export type LibraryList = { results: LibraryItem[]; count: number; page: number; pages: number };
export type LibraryParams = { kind: LibraryFilter; page: number; q: string };
export type LibraryPracticeStats = {
  totalCount: number;
  studiedCount: number;
  dueCount: number;
  answers: number;
  accuracy: number;
  audioCount?: number;
};
export type LibraryQuizType =
  | 'arabic_meaning'
  | 'meaning_arabic'
  | 'arabic_title'
  | 'title_arabic'
  | 'audio_arabic'
  | 'audio_meaning';
export type LibraryQuestion = {
  id: string;
  prompt: string;
  quizType: LibraryQuizType;
  options: { label: string }[];
  audioTracks?: AudioTrack[];
};
export type LibraryQuizResult = {
  accepted: boolean;
  isCorrect: boolean;
  correctOption: number;
  answerLabel: string;
  answerMeaning: string;
};
