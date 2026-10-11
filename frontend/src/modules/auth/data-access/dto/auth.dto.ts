export interface ProfileDto {
  id: number;
  first_name: string;
  username: string;
  language: 'uz' | 'ru' | 'en';
  timezone: string;
  account_kind: 'guest' | 'member' | 'telegram';
  is_guest: boolean;
  email: string;
  telegram_linked: boolean;
}
export interface SessionDto {
  authenticated: boolean;
  profile: ProfileDto | null;
  bot_username: string;
}
export interface ChallengeDto {
  telegram_url: string;
  expires_at: string;
  verification_code: string;
}
export interface CompletionDto {
  status?: 'pending';
  profile?: ProfileDto;
}
