export type PrayerType = 'fajr' | 'dhuhr' | 'asr' | 'maghrib' | 'isha';
export type CurrentQada = {
  key: string;
  source: 'manual' | 'historical';
  prayerDate: string;
  prayerType: PrayerType;
};
export type QadaRecord = {
  id: number;
  source: 'manual' | 'historical';
  prayerDate: string;
  prayerType: PrayerType;
  status: string;
  completedAt: string | null;
};
export type QadaSummary = {
  current: CurrentQada | null;
  manualPending: number;
  manualCompleted: number;
  historicalCompleted: number;
  historicalConfigured: boolean;
  fastBalance: number;
  manualQueue: QadaRecord[];
  history: QadaRecord[];
};
export type QadaConfigure = { startDate: string; startPrayer: PrayerType };
export type QadaAdd = { prayerDate: string; prayerType: PrayerType };
export type FastAction = { action: 'add' | 'complete'; amount: number; operationId: string };
export type FastIntent = Omit<FastAction, 'operationId'>;
