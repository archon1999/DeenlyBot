import type { AudioTrack } from 'src/shared/domain/audio';

export type NameStatus = 'new' | 'learning' | 'learned';
export type NameQuizType = 'name_meaning' | 'meaning_name' | 'number_name' | 'name_number';
export type AllahName = {
  id: number;
  order: number;
  arabic: string;
  transcription: string;
  meaning: string;
  description: string;
  status: NameStatus;
  isNext: boolean;
  audioTracks?: AudioTrack[];
};
export type NamesOverview = {
  results: AllahName[];
  total: number;
  introducedCount: number;
  learnedCount: number;
  dueCount: number;
  nextId: number | null;
};
export type NameQuestion = {
  id: string;
  prompt: string;
  quizType: NameQuizType;
  options: { label: string }[];
};
export type NameQuizResult = {
  accepted: boolean;
  isCorrect: boolean;
  correctOption: number;
  answerLabel: string;
  answerMeaning: string;
};
export type NameQuiz = { question: NameQuestion | null; requiredNames: number };
