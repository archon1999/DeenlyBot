import type { DashboardDto } from '../dto';
import type { DashboardRepository } from '../../domain';

import { apiClient } from 'src/shared/api';

import { mapDashboard } from '../mappers';

export const dashboardRepository: DashboardRepository = {
  overview: async () => mapDashboard(await apiClient.get<DashboardDto>('dashboard/')),
};
