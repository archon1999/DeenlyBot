import type {
  Profile,
  AuthSession,
  ProfileUpdate,
  LoginChallenge,
  LoginCompletion,
  ProfileLanguage,
  GuestEntryInput,
  RegistrationInput,
  AccountLoginInput,
} from '../entities/auth.types';

export interface AuthRepository {
  session(): Promise<AuthSession>;
  guest(input: GuestEntryInput): Promise<Profile>;
  register(input: RegistrationInput): Promise<Profile>;
  login(input: AccountLoginInput): Promise<Profile>;
  profile(): Promise<Profile>;
  updateProfile(input: ProfileUpdate): Promise<Profile>;
  startLogin(): Promise<LoginChallenge>;
  completeLogin(): Promise<LoginCompletion>;
  startTelegramLink(): Promise<LoginChallenge>;
  completeTelegramLink(): Promise<LoginCompletion>;
  miniApp(initData: string): Promise<Profile>;
  logout(): Promise<void>;
  setLanguage(language: ProfileLanguage): Promise<void>;
}
