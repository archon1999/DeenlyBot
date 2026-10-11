import type { QadaAdd, FastAction, QadaSummary, QadaConfigure } from '../entities';

export interface WorshipRepository {
  summary(): Promise<QadaSummary>;
  configure(params: QadaConfigure): Promise<QadaSummary>;
  add(params: QadaAdd): Promise<QadaSummary>;
  complete(key: string): Promise<QadaSummary>;
  fast(params: FastAction): Promise<QadaSummary>;
}
