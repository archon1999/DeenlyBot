import type {
  LibraryItemDto,
  LibraryListDto,
  LibraryQuizDto,
  LibraryResultDto,
  LibraryDetailDto,
  LibraryPracticeDto,
} from '../dto';
import type {
  LibraryItem,
  LibraryList,
  LibraryDetail,
  LibraryQuestion,
  LibraryQuizResult,
  LibraryPracticeStats,
} from '../../domain';

import { mapAudioTracks } from 'src/shared/audio/audio.dto';

export const mapLibraryItem = (d: LibraryItemDto): LibraryItem => ({
  id: d.id,
  kind: d.kind,
  title: d.title,
  arabicText: d.arabic_text,
  transcription: d.transcription,
  translation: d.translation,
  reference: d.reference,
  isFavorite: d.is_favorite,
  isStudied: d.is_studied ?? false,
  audioTracks: mapAudioTracks(d.audio_tracks),
});
export const mapLibraryDetail = (d: LibraryDetailDto): LibraryDetail => ({
  ...mapLibraryItem(d),
  analysis: d.analysis
    ? {
        summary: d.analysis.summary,
        context: d.analysis.context,
        explanation: d.analysis.explanation,
        verses: d.analysis.verses.map((verse) => ({
          key: verse.key,
          arabicText: verse.arabic_text,
          translation: verse.translation,
          transcription: verse.transcription,
          words: verse.words.map((word) => ({
            id: String(word.id),
            arabicText: word.arabic_text,
            root: word.root,
            meaning: word.meaning,
            transcription: word.transcription,
            grammarNote: word.grammar_note,
          })),
        })),
      }
    : null,
});
export const mapLibraryPractice = (d: LibraryPracticeDto): LibraryPracticeStats => ({
  totalCount: d.stats.total_count,
  studiedCount: d.stats.studied_count,
  dueCount: d.stats.due_count,
  answers: d.stats.answers,
  accuracy: d.stats.accuracy,
  audioCount: d.stats.audio_count ?? 0,
});
export const mapLibraryQuiz = (d: LibraryQuizDto): LibraryQuestion | null =>
  d.question
    ? {
        id: d.question.id,
        prompt: d.question.prompt,
        quizType: d.question.quiz_type,
        options: d.question.options.map((option) => ({ label: option.label })),
        audioTracks: mapAudioTracks(d.question.audio_tracks),
      }
    : null;
export const mapLibraryResult = (d: LibraryResultDto): LibraryQuizResult => ({
  accepted: d.accepted,
  isCorrect: d.is_correct,
  correctOption: d.correct_option,
  answerLabel: d.answer_label,
  answerMeaning: d.answer_meaning,
});
export const mapLibraryList = (d: LibraryListDto): LibraryList => ({
  results: d.results.map(mapLibraryItem),
  count: d.count,
  page: d.page,
  pages: d.pages,
});
