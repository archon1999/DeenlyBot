import type { QadaRecord, CurrentQada, QadaSummary } from '../../domain';
import type { QadaRecordDto, CurrentQadaDto, QadaSummaryDto } from '../dto';

export const mapCurrentQada = (d: CurrentQadaDto): CurrentQada => ({
  key: d.key,
  source: d.source,
  prayerDate: d.prayer_date,
  prayerType: d.prayer_type,
});
const mapRecord = (d: QadaRecordDto): QadaRecord => ({
  id: d.id,
  source: d.source,
  prayerDate: d.prayer_date,
  prayerType: d.prayer_type,
  status: d.status,
  completedAt: d.completed_at,
});
export const mapQada = (d: QadaSummaryDto): QadaSummary => ({
  current: d.current ? mapCurrentQada(d.current) : null,
  manualPending: d.manual_pending,
  manualCompleted: d.manual_completed,
  historicalCompleted: d.historical_completed,
  historicalConfigured: d.historical_configured,
  fastBalance: d.fast_balance,
  manualQueue: d.manual_queue.map(mapRecord),
  history: d.history.map(mapRecord),
});
