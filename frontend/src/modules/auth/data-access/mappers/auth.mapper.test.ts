import { it, expect, describe } from 'vitest';

import { ApiError } from 'src/shared/api';

import { AuthFormError } from '../../domain';
import {
  mapProfile,
  mapChallenge,
  mapAuthError,
  mapCompletion,
  profilePayload,
  registrationPayload,
} from './auth.mapper';

const dto = {
  id: 42,
  first_name: 'Laylo',
  username: '',
  language: 'uz' as const,
  timezone: 'Asia/Tashkent',
  account_kind: 'guest' as const,
  is_guest: true,
  email: '',
  telegram_linked: false,
};
describe('auth identity transport boundary', () => {
  it('keeps the browser verification code as text including leading zeroes', () => {
    const challenge = mapChallenge({
      telegram_url: 'https://t.me/test_bot?start=web_token',
      expires_at: '2026-10-11T20:00:00Z',
      verification_code: '00AF12',
    });
    expect(challenge.verificationCode).toBe('00AF12');
  });
  it('keeps guest identity separate from verified Telegram/member capability flags', () => {
    const profile = mapProfile(dto);
    expect(profile.id).toBe(42);
    expect(profile.isGuest).toBe(true);
    expect(profile.telegramLinked).toBe(false);
    expect(profile.email).toBe('');
    const member = mapProfile({
      ...dto,
      account_kind: 'member',
      is_guest: false,
      email: 'laylo@example.com',
      telegram_linked: true,
    });
    expect(member.accountKind).toBe('member');
    expect(member.isGuest).toBe(false);
    expect(member.telegramLinked).toBe(true);
  });
  it('keeps pending approval distinct from a verified profile response', () => {
    expect(mapCompletion({ status: 'pending' })).toEqual({ status: 'pending', profile: null });
    expect(mapCompletion({ profile: dto }).status).toBe('approved');
  });
  it('maps user form intents without altering the chosen password', () => {
    expect(
      registrationPayload({
        email: ' laylo@example.com ',
        firstName: ' Laylo ',
        password: '  keep spaces  ',
        language: 'uz',
      })
    ).toEqual({
      email: 'laylo@example.com',
      first_name: 'Laylo',
      password: '  keep spaces  ',
      language: 'uz',
    });
    expect(profilePayload({ firstName: ' Laylo ' })).toEqual({ first_name: 'Laylo' });
  });
  it('maps field errors to domain names instead of exposing snake-case fields in UI', () => {
    const error = mapAuthError(
      new ApiError(400, { first_name: ['Required'], password: ['Too common'] })
    );
    expect(error).toBeInstanceOf(AuthFormError);
    expect((error as AuthFormError).fields).toEqual({
      firstName: 'Required',
      password: 'Too common',
    });
  });
});
