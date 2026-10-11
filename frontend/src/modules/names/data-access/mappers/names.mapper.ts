import type { NameDto, NamesDto, NameQuizDto, NameResultDto } from '../dto';
import type { NameQuiz, AllahName, NamesOverview, NameQuizResult } from '../../domain';

import { mapAudioTracks } from 'src/shared/audio/audio.dto';

export const mapName = (d: NameDto): AllahName => ({
  id: d.id,
  order: d.order,
  arabic: d.arabic,
  transcription: d.transcription,
  meaning: d.meaning,
  description: d.description,
  status: d.status,
  isNext: d.is_next,
  audioTracks: mapAudioTracks(d.audio_tracks),
});
export const mapNames = (d: NamesDto): NamesOverview => ({
  results: d.results.map(mapName),
  total: d.total,
  introducedCount: d.introduced_count,
  learnedCount: d.learned_count,
  dueCount: d.due_count,
  nextId: d.next_id,
});
export const mapQuiz = (d: NameQuizDto): NameQuiz => ({
  requiredNames: d.required_names,
  question: d.question
    ? {
        id: d.question.id,
        prompt: d.question.prompt,
        quizType: d.question.quiz_type,
        options: d.question.options,
      }
    : null,
});
export const mapResult = (d: NameResultDto): NameQuizResult => ({
  accepted: d.accepted,
  isCorrect: d.is_correct,
  correctOption: d.correct_option,
  answerLabel: d.answer_label,
  answerMeaning: d.answer_meaning,
});
