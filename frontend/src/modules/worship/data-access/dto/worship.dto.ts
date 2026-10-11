import type { PrayerType } from '../../domain';

export type CurrentQadaDto = {
  key: string;
  source: 'manual' | 'historical';
  prayer_date: string;
  prayer_type: PrayerType;
};
export type QadaRecordDto = {
  id: number;
  source: 'manual' | 'historical';
  prayer_date: string;
  prayer_type: PrayerType;
  status: string;
  completed_at: string | null;
};
export type QadaSummaryDto = {
  current: CurrentQadaDto | null;
  manual_pending: number;
  manual_completed: number;
  historical_completed: number;
  historical_configured: boolean;
  fast_balance: number;
  manual_queue: QadaRecordDto[];
  history: QadaRecordDto[];
};
