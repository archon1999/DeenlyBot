import type { DashboardOverview } from '../entities';

export interface DashboardRepository {
  overview(): Promise<DashboardOverview>;
}
