import type { ProfileDto, SessionDto, ChallengeDto, CompletionDto } from '../dto/auth.dto';
import type {
  Profile,
  AuthSession,
  ProfileUpdate,
  LoginChallenge,
  LoginCompletion,
  AuthFieldErrors,
  RegistrationInput,
} from '../../domain';

import { ApiError } from 'src/shared/api';

import { AuthFormError } from '../../domain';

export const mapProfile = (dto: ProfileDto): Profile => ({
  id: dto.id,
  firstName: dto.first_name,
  username: dto.username,
  language: dto.language,
  timezone: dto.timezone,
  accountKind: dto.account_kind,
  isGuest: dto.is_guest,
  email: dto.email,
  telegramLinked: dto.telegram_linked,
});
export const mapSession = (dto: SessionDto): AuthSession => ({
  authenticated: dto.authenticated,
  profile: dto.profile ? mapProfile(dto.profile) : null,
  botUsername: dto.bot_username,
});
export const mapChallenge = (dto: ChallengeDto): LoginChallenge => ({
  telegramUrl: dto.telegram_url,
  expiresAt: dto.expires_at,
  verificationCode: dto.verification_code,
});
export const mapCompletion = (dto: CompletionDto): LoginCompletion => ({
  status: dto.profile ? 'approved' : 'pending',
  profile: dto.profile ? mapProfile(dto.profile) : null,
});
export const registrationPayload = (input: RegistrationInput) => ({
  email: input.email.trim(),
  password: input.password,
  first_name: input.firstName.trim(),
  ...(input.language ? { language: input.language } : {}),
});
export const profilePayload = (input: ProfileUpdate) => ({
  ...(input.firstName !== undefined ? { first_name: input.firstName.trim() } : {}),
  ...(input.language !== undefined ? { language: input.language } : {}),
  ...(input.timezone !== undefined ? { timezone: input.timezone.trim() } : {}),
});
export function mapAuthError(error: unknown): unknown {
  if (!(error instanceof ApiError)) return error;
  const keys = {
    email: 'email',
    password: 'password',
    first_name: 'firstName',
    language: 'language',
    timezone: 'timezone',
  } as const;
  const fields: AuthFieldErrors = {};
  for (const [key, value] of Object.entries(error.details)) {
    const target = keys[key as keyof typeof keys];
    if (target) fields[target] = Array.isArray(value) ? value.join(' ') : String(value);
  }
  return new AuthFormError(error.message, fields, error.status);
}
