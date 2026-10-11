import { useNavigate } from 'react-router';

import { Alert, Stack, Button, Typography } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { useAuthLabels } from '../../../labels';
import { useSession, useGuestEntry } from '../../../../application';

export function GuestEntry({ redirect, compact = false }: { redirect: string; compact?: boolean }) {
  const labels = useAuthLabels();
  const { language } = useLocale();
  const session = useSession();
  const mutation = useGuestEntry();
  const navigate = useNavigate();
  const enter = () => {
    if (session.profile?.isGuest) navigate(redirect, { replace: true });
    else mutation.mutate({ language }, { onSuccess: () => navigate(redirect, { replace: true }) });
  };
  return (
    <Stack spacing={1.5}>
      <Button
        size={compact ? 'medium' : 'large'}
        color="inherit"
        onClick={enter}
        loading={mutation.isPending}
        startIcon={<OutlineIcon name="guest" width={20} />}
        sx={{ fontWeight: 500 }}
      >
        {session.profile?.isGuest ? labels.guestContinue : labels.guestAction}
      </Button>
      {!compact && (
        <Typography
          variant="caption"
          color="text.secondary"
          textAlign="center"
          sx={{ lineHeight: 1.8 }}
        >
          {labels.guestHint}
        </Typography>
      )}
      {mutation.error && <Alert severity="error">{mutation.error.message}</Alert>}
    </Stack>
  );
}
