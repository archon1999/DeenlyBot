import type { AudioTrackDto } from 'src/shared/audio/audio.dto';

export type NameDto = {
  id: number;
  order: number;
  arabic: string;
  transcription: string;
  meaning: string;
  description: string;
  status: 'new' | 'learning' | 'learned';
  is_next: boolean;
  audio_tracks?: AudioTrackDto[];
};
export type NamesDto = {
  results: NameDto[];
  total: number;
  introduced_count: number;
  learned_count: number;
  due_count: number;
  next_id: number | null;
};
export type NameQuestionDto = {
  id: string;
  prompt: string;
  quiz_type: 'name_meaning' | 'meaning_name' | 'number_name' | 'name_number';
  options: { label: string }[];
};
export type NameQuizDto = { question: NameQuestionDto | null; required_names: number };
export type NameResultDto = {
  accepted: boolean;
  is_correct: boolean;
  correct_option: number;
  answer_label: string;
  answer_meaning: string;
};
