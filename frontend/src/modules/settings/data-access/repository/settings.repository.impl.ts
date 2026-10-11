import type { SettingsDto } from '../dto';
import type { SettingsRepository } from '../../domain';

import { apiClient } from 'src/shared/api';

import { mapSettings, settingsPayload } from '../mappers';

export const settingsRepository: SettingsRepository = {
  get: async () => mapSettings(await apiClient.get<SettingsDto>('settings/')),
  save: async (p) =>
    mapSettings(await apiClient.patch<SettingsDto>('settings/', settingsPayload(p))),
};
