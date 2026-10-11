import type { ReportsDto } from '../dto';
import type { ReportsRepository } from '../../domain';

import { apiClient } from 'src/shared/api';

import { mapReports } from '../mappers';

export const reportsRepository: ReportsRepository = {
  overview: async () => mapReports(await apiClient.get<ReportsDto>('reports/')),
};
