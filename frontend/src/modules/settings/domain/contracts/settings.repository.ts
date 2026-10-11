import type { UserSettings } from '../entities';

export interface SettingsRepository {
  get(): Promise<UserSettings>;
  save(params: UserSettings): Promise<UserSettings>;
}
