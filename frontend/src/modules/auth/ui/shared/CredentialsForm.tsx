import type { AuthLabels } from '../labels';

import { useState } from 'react';

import { Box, Alert, Stack, Button, TextField, InputAdornment } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { AuthFormError } from '../../domain';
import { useAccountLogin, useRegisterAccount, useProfileNameDraft } from '../../application';

type Props = {
  mode: 'login' | 'register';
  labels: AuthLabels;
  initialFirstName?: string;
  submitLabel?: string;
  onCompleted?: () => void;
  compact?: boolean;
};
export function CredentialsForm({
  mode,
  labels,
  initialFirstName = '',
  submitLabel,
  onCompleted,
  compact = false,
}: Props) {
  const login = useAccountLogin();
  const register = useRegisterAccount();
  const mutation = mode === 'register' ? register : login;
  const { language } = useLocale();
  const { name: firstName, setName: setFirstName } = useProfileNameDraft(initialFirstName);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const fields = mutation.error instanceof AuthFormError ? mutation.error.fields : {};
  const resetError = () => {
    login.reset();
    register.reset();
  };
  const submit = () => {
    const onSuccess = () => {
      setPassword('');
      onCompleted?.();
    };
    if (mode === 'register')
      register.mutate({ email, password, firstName, language }, { onSuccess });
    else login.mutate({ email, password }, { onSuccess });
  };
  return (
    <Box
      component="form"
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
    >
      <Stack
        spacing={compact ? 2 : 2.5}
        sx={compact ? { '@media (max-height:700px)': { gap: 1 } } : undefined}
      >
        {mode === 'register' && (
          <TextField
            size="medium"
            label={labels.firstName}
            value={firstName}
            onChange={(event) => {
              setFirstName(event.target.value);
              resetError();
            }}
            autoComplete="given-name"
            required
            error={Boolean(fields.firstName)}
            helperText={fields.firstName}
            slotProps={{
              htmlInput: { maxLength: 128 },
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <OutlineIcon name="user" width={20} />
                  </InputAdornment>
                ),
              },
            }}
          />
        )}
        <TextField
          size="medium"
          label={labels.email}
          type="email"
          value={email}
          onChange={(event) => {
            setEmail(event.target.value);
            resetError();
          }}
          autoComplete="email"
          required
          error={Boolean(fields.email)}
          helperText={fields.email}
          slotProps={{
            htmlInput: { maxLength: 254 },
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <OutlineIcon name="email" width={20} />
                </InputAdornment>
              ),
            },
          }}
        />
        <TextField
          size="medium"
          label={labels.password}
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(event) => {
            setPassword(event.target.value);
            resetError();
          }}
          autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
          required
          error={Boolean(fields.password)}
          helperText={fields.password ?? (mode === 'register' ? labels.passwordHint : undefined)}
          slotProps={{
            htmlInput: { minLength: mode === 'register' ? 8 : undefined, maxLength: 128 },
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <OutlineIcon name="lock" width={20} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <Button
                    type="button"
                    color="inherit"
                    size="small"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={showPassword ? labels.hide : labels.show}
                    sx={{ minWidth: 0, fontSize: 12 }}
                  >
                    {showPassword ? labels.hide : labels.show}
                  </Button>
                </InputAdornment>
              ),
            },
          }}
        />
        {mutation.error && <Alert severity="error">{mutation.error.message}</Alert>}
        <Button
          type="submit"
          variant="contained"
          size={compact ? 'medium' : 'large'}
          loading={mutation.isPending}
          endIcon={<OutlineIcon name={mode === 'register' ? 'check' : 'login'} width={20} />}
          sx={{ fontWeight: 500 }}
        >
          {submitLabel ?? (mode === 'register' ? labels.register : labels.login)}
        </Button>
      </Stack>
    </Box>
  );
}
