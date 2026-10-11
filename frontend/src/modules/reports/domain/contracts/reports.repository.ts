import type { ReportsOverview } from '../entities';

export interface ReportsRepository {
  overview(): Promise<ReportsOverview>;
}
