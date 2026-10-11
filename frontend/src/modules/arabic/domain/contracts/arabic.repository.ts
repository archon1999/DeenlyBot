import type { PracticeMode } from 'src/shared/domain/audio';
import type {
  ArabicOverview,
  ArabicQuestion,
  ArabicQuizResult,
  ArabicLessonDetail,
} from '../entities';

export interface ArabicRepository {
  overview(): Promise<ArabicOverview>;
  lesson(id: number): Promise<ArabicLessonDetail>;
  start(id: number): Promise<{ status: string }>;
  complete(id: number): Promise<{ status: string }>;
  quiz(extra: boolean, mode?: PracticeMode): Promise<ArabicQuestion | null>;
  answer(id: string, option: number): Promise<ArabicQuizResult>;
}
