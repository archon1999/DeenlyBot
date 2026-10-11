import type { PracticeMode } from 'src/shared/domain/audio';
import type {
  LibraryList,
  LibraryKind,
  LibraryParams,
  LibraryFilter,
  LibraryDetail,
  LibraryQuestion,
  LibraryQuizResult,
  LibraryPracticeStats,
} from '../entities';

export interface LibraryRepository {
  list(params: LibraryParams): Promise<LibraryList>;
  detail(kind: LibraryKind, id: number): Promise<LibraryDetail>;
  favorite(kind: LibraryKind, id: number, saved: boolean): Promise<{ saved: boolean }>;
  study(kind: LibraryKind, id: number): Promise<{ created: boolean; isStudied: boolean }>;
  practice(kind: LibraryFilter): Promise<LibraryPracticeStats>;
  quiz(
    kind: LibraryFilter,
    extra: boolean,
    mode?: PracticeMode,
    itemId?: number
  ): Promise<LibraryQuestion | null>;
  answer(id: string, option: number): Promise<LibraryQuizResult>;
}
