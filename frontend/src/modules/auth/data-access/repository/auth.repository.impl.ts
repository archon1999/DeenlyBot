import type { AuthRepository } from '../../domain';
import type { ProfileDto, SessionDto, ChallengeDto, CompletionDto } from '../dto/auth.dto';

import { apiClient } from 'src/shared/api';

import {
  mapProfile,
  mapSession,
  mapChallenge,
  mapAuthError,
  mapCompletion,
  profilePayload,
  registrationPayload,
} from '../mappers/auth.mapper';

async function profileCommand(path: string, payload: unknown = {}) {
  try {
    return mapProfile((await apiClient.post<{ profile: ProfileDto }>(path, payload)).profile);
  } catch (error) {
    throw mapAuthError(error);
  }
}
export const authRepository: AuthRepository = {
  session: async () => mapSession(await apiClient.get<SessionDto>('auth/session/')),
  guest: (input) => profileCommand('auth/guest/', input),
  register: (input) => profileCommand('auth/register/', registrationPayload(input)),
  login: (input) =>
    profileCommand('auth/login/', { email: input.email.trim(), password: input.password }),
  profile: async () =>
    mapProfile((await apiClient.get<{ profile: ProfileDto }>('auth/profile/')).profile),
  updateProfile: async (input) => {
    try {
      return mapProfile(
        (await apiClient.patch<{ profile: ProfileDto }>('auth/profile/', profilePayload(input)))
          .profile
      );
    } catch (error) {
      throw mapAuthError(error);
    }
  },
  startLogin: async () => mapChallenge(await apiClient.post<ChallengeDto>('auth/telegram/start/')),
  completeLogin: async () =>
    mapCompletion(await apiClient.post<CompletionDto>('auth/telegram/complete/')),
  startTelegramLink: async () =>
    mapChallenge(await apiClient.post<ChallengeDto>('auth/telegram/link/start/')),
  completeTelegramLink: async () =>
    mapCompletion(await apiClient.post<CompletionDto>('auth/telegram/link/complete/')),
  miniApp: (initData) => profileCommand('auth/miniapp/', { init_data: initData }),
  logout: async () => {
    await apiClient.post('auth/logout/');
  },
  setLanguage: async (language) => {
    await apiClient.patch('settings/', { language });
  },
};
