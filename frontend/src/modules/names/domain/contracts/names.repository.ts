import type { NameQuiz, NamesOverview, NameQuizResult } from '../entities';

export interface NamesRepository {
  overview(): Promise<NamesOverview>;
  confirm(id: number): Promise<{ created: boolean }>;
  quiz(extraPractice: boolean): Promise<NameQuiz>;
  answer(id: string, option: number): Promise<NameQuizResult>;
}
