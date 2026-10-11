export type ProfileLanguage = 'uz' | 'ru' | 'en';
export type AccountKind = 'guest' | 'member' | 'telegram';
export interface Profile {
  id: number;
  firstName: string;
  username: string;
  language: ProfileLanguage;
  timezone: string;
  accountKind: AccountKind;
  isGuest: boolean;
  email: string;
  telegramLinked: boolean;
}
export interface AuthSession {
  authenticated: boolean;
  profile: Profile | null;
  botUsername: string;
}
export interface LoginChallenge {
  telegramUrl: string;
  expiresAt: string;
  verificationCode: string;
}
export interface LoginCompletion {
  status: 'pending' | 'approved';
  profile: Profile | null;
}
export interface GuestEntryInput {
  language: ProfileLanguage;
  timezone?: string;
}
export interface RegistrationInput {
  email: string;
  password: string;
  firstName: string;
  language?: ProfileLanguage;
}
export interface AccountLoginInput {
  email: string;
  password: string;
}
export interface ProfileUpdate {
  firstName?: string;
  language?: ProfileLanguage;
  timezone?: string;
}
export type AuthFieldErrors = Partial<
  Record<'email' | 'password' | 'firstName' | 'language' | 'timezone', string>
>;
export class AuthFormError extends Error {
  constructor(
    message: string,
    public fields: AuthFieldErrors = {},
    public status?: number
  ) {
    super(message);
    this.name = 'AuthFormError';
  }
}
