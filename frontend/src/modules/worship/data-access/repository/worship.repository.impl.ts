import type { QadaSummaryDto } from '../dto';
import type { WorshipRepository } from '../../domain';

import { apiClient } from 'src/shared/api';

import { mapQada } from '../mappers';

export const worshipRepository: WorshipRepository = {
  summary: async () => mapQada(await apiClient.get<QadaSummaryDto>('qada/')),
  configure: async (p) =>
    mapQada(
      await apiClient.post<QadaSummaryDto>('qada/configure/', {
        start_date: p.startDate,
        start_prayer: p.startPrayer,
      })
    ),
  add: async (p) =>
    mapQada(
      await apiClient.post<QadaSummaryDto>('qada/add/', {
        prayer_date: p.prayerDate,
        prayer_type: p.prayerType,
      })
    ),
  complete: async (key) =>
    mapQada(await apiClient.post<QadaSummaryDto>('qada/complete/', { expected_key: key })),
  fast: async (p) =>
    mapQada(
      await apiClient.post<QadaSummaryDto>('qada/fast/', {
        action: p.action,
        amount: p.amount,
        operation_id: p.operationId,
      })
    ),
};
