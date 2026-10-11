import type {
  AuthSession,
  ProfileUpdate,
  ProfileLanguage,
  GuestEntryInput,
  RegistrationInput,
  AccountLoginInput,
} from '../domain';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { authKeys } from './keys';
import { authRepository } from '../data-access';
import { enterGuestOnce, enterMiniAppOnce } from './guest-session';
import { applySignedOutSession, applyAuthenticatedProfile } from './session-cache';

export function useGuestEntry() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: GuestEntryInput) =>
      enterGuestOnce(authRepository, input, client.getQueryData<AuthSession>(authKeys.session)),
    onSuccess: (profile) => applyAuthenticatedProfile(client, profile),
  });
}
export function useRegisterAccount() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: RegistrationInput) => authRepository.register(input),
    onSuccess: (profile) => applyAuthenticatedProfile(client, profile),
  });
}
export function useAccountLogin() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: AccountLoginInput) => authRepository.login(input),
    onSuccess: (profile) => applyAuthenticatedProfile(client, profile),
  });
}
export function useUpdateProfile() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: ProfileUpdate) => authRepository.updateProfile(input),
    onSuccess: (profile) => applyAuthenticatedProfile(client, profile),
  });
}
export function useStartLogin() {
  return useMutation({ mutationFn: () => authRepository.startLogin() });
}
export function useCompleteLogin() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => authRepository.completeLogin(),
    onSuccess: (result) =>
      result.profile ? applyAuthenticatedProfile(client, result.profile) : undefined,
  });
}
export function useStartTelegramLink() {
  return useMutation({ mutationFn: () => authRepository.startTelegramLink() });
}
export function useCompleteTelegramLink() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => authRepository.completeTelegramLink(),
    onSuccess: (result) =>
      result.profile ? applyAuthenticatedProfile(client, result.profile) : undefined,
  });
}
export function useMiniAppLogin(preserveExisting = false) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (initData: string) =>
      enterMiniAppOnce(
        authRepository,
        initData,
        preserveExisting ? client.getQueryData<AuthSession>(authKeys.session) : undefined
      ),
    onSuccess: (profile) => applyAuthenticatedProfile(client, profile),
  });
}
export function useLogout() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: authRepository.logout,
    onSuccess: () => applySignedOutSession(client),
  });
}
export function useLanguagePreference() {
  const client = useQueryClient();
  const { setLanguage } = useLocale();
  return useMutation({
    mutationFn: (language: ProfileLanguage) => authRepository.setLanguage(language),
    onSuccess: async (_, language) => {
      setLanguage(language);
      await client.invalidateQueries();
    },
  });
}
