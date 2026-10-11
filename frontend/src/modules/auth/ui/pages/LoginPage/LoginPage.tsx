import { varAlpha } from 'minimal-shared/utils';
import { Navigate, useNavigate, useSearchParams } from 'react-router';

import { Box, Stack, Divider, Typography } from '@mui/material';

import { Logo } from 'src/shared/ui/logo';
import { QueryState } from 'src/shared/ui/query-state';
import { LearningTabs } from 'src/shared/ui/learning-tabs';
import { ThemeButton } from 'src/app/layouts/components/theme-button';
import { LanguagePopover } from 'src/app/layouts/components/language-popover';

import { useAuthLabels } from '../../labels';
import { GuestEntry } from './components/GuestEntry';
import { TelegramLogin } from './components/TelegramLogin';
import { CredentialsForm } from '../../shared/CredentialsForm';
import { useSession, safeReturnPath } from '../../../application';
import { AuthWelcome, AuthIllustration } from './components/AuthWelcome';

/** Desktop stays centered; mobile starts below the header with height-aware artwork and spacing. */
export function LoginPage() {
  const session = useSession();
  const [params, setParams] = useSearchParams();
  const labels = useAuthLabels();
  const navigate = useNavigate();
  const safeRedirect = safeReturnPath(params.get('next'), window.location.origin);
  const mode = params.get('mode') === 'register' ? 'register' : 'login';
  if (session.authenticated && !session.profile?.isGuest)
    return <Navigate to={safeRedirect} replace />;
  const setMode = (value: string) => {
    const next = new URLSearchParams(params);
    next.set('mode', value);
    setParams(next, { replace: true });
  };
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          md: 'minmax(0,1fr) minmax(0,1fr)',
          lg: 'minmax(0,1.05fr) minmax(0,1fr)',
        },
        height: '100dvh',
        minHeight: 0,
        overflow: 'hidden',
        bgcolor: 'background.paper',
      }}
    >
      <AuthWelcome labels={labels} />
      <Box
        component="main"
        sx={(theme) => ({
          height: '100dvh',
          minHeight: 0,
          minWidth: 0,
          overflowY: 'auto',
          overscrollBehavior: 'contain',
          p: { xs: 1.5, sm: 2, md: 2 },
          display: 'flex',
          flexDirection: 'column',
          bgcolor: {
            xs: varAlpha(theme.vars.palette.primary.mainChannel, 0.035),
            md: 'background.paper',
          },
          ...theme.applyStyles('dark', {
            bgcolor: {
              xs: varAlpha(theme.vars.palette.primary.mainChannel, 0.06),
              md: 'background.paper',
            },
          }),
        })}
      >
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          spacing={2}
          sx={{ width: 1, maxWidth: 520, mx: 'auto', mb: 0.5, flexShrink: 0 }}
        >
          <Box sx={{ display: { md: 'none' } }}>
            <Logo isSingle={false} />
          </Box>
          <Box sx={{ display: { xs: 'none', md: 'block' } }} />
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <ThemeButton />
            <LanguagePopover persist={session.authenticated} />
          </Stack>
        </Stack>
        <Box
          data-testid="auth-mobile-art"
          sx={{
            display: { xs: 'block', md: 'none' },
            color: 'primary.main',
            width: 180,
            height: 96,
            mx: 'auto',
            mt: 1,
            mb: 1,
            flexShrink: 0,
            '& svg': { display: 'block', height: 1 },
            '@media (max-height:799px)': { display: 'none' },
          }}
        >
          <AuthIllustration maxHeight="96px" />
        </Box>
        <Box
          data-testid="auth-form-block"
          sx={(theme) => ({
            width: 1,
            maxWidth: 420,
            mx: 'auto',
            mt: { xs: 1, md: 'auto' },
            mb: { xs: 0, md: 'auto' },
            px: { xs: 2.5, md: 0 },
            py: { xs: 2.5, md: 0.5 },
            borderRadius: { xs: 2.5, md: 0 },
            bgcolor: { xs: 'background.paper', md: 'transparent' },
            boxShadow: { xs: theme.vars.customShadows.card, md: 'none' },
            flexShrink: 0,
            '@media (max-height:700px)': {
              px: { xs: 1.5, md: 0 },
              py: { xs: 1.5, md: 0.5 },
              mt: { xs: 0.5, md: 'auto' },
            },
          })}
        >
          <Typography
            variant="h4"
            sx={{
              fontWeight: 500,
              lineHeight: 1.25,
              mb: 2,
              fontSize: { xs: 22, md: 28 },
              '@media (max-height:700px)': { mb: 1 },
            }}
          >
            {labels.welcome}
          </Typography>
          <QueryState
            isPending={session.isLoading}
            error={session.error}
            onRetry={session.refreshSession}
          >
            <Box sx={{ mb: 2.5, '@media (max-height:700px)': { mb: 1 } }}>
              <LearningTabs
                value={mode}
                onChange={setMode}
                label={labels.welcome}
                items={[
                  { key: 'login', title: labels.login },
                  { key: 'register', title: labels.register },
                ]}
              />
            </Box>
            <CredentialsForm
              compact
              key={mode}
              mode={mode}
              labels={labels}
              initialFirstName={session.profile?.firstName}
              onCompleted={() => navigate(safeRedirect, { replace: true })}
            />
            <Divider sx={{ my: 1.5, '@media (max-height:700px)': { my: 0.5 } }}>
              <Typography variant="caption" color="text.secondary">
                {labels.or}
              </Typography>
            </Divider>
            <TelegramLogin compact onCompleted={() => navigate(safeRedirect, { replace: true })} />
            <Box sx={{ mt: 1.5, '@media (max-height:700px)': { mt: 0.5 } }}>
              <GuestEntry compact redirect={safeRedirect} />
            </Box>
          </QueryState>
        </Box>
      </Box>
    </Box>
  );
}
