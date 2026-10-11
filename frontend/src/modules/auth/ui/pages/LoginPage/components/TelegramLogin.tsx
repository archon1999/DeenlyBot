import { useEffect } from 'react';

import { Alert, Stack, Button, Typography, CircularProgress } from '@mui/material';

import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { useAuthLabels } from '../../../labels';
import { useTelegramLoginFlow } from '../../../../application';
import { VerificationCode } from '../../../shared/VerificationCode';

export function TelegramLogin({
  onCompleted,
  compact = false,
}: {
  onCompleted: () => void;
  compact?: boolean;
}) {
  const labels = useAuthLabels();
  const flow = useTelegramLoginFlow();
  useEffect(() => {
    if (flow.approved || flow.isMiniAppApproved) onCompleted();
  }, [flow.approved, flow.isMiniAppApproved, onCompleted]);
  return (
    <Stack spacing={1.5}>
      {flow.error instanceof Error && <Alert severity="error">{flow.error.message}</Alert>}
      {flow.expired && <Alert severity="warning">{labels.telegramExpired}</Alert>}
      {flow.isMiniAppPending && (
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <CircularProgress size={20} />
          <Typography variant="body2">{labels.telegramMini}</Typography>
        </Stack>
      )}
      {flow.waiting ? (
        <>
          {flow.challenge && (
            <VerificationCode code={flow.challenge.verificationCode} labels={labels} />
          )}
          <Button
            component="a"
            href={flow.challenge?.telegramUrl}
            target="_blank"
            rel="noopener noreferrer"
            size={compact ? 'medium' : 'large'}
            variant="outlined"
            color="inherit"
            startIcon={<OutlineIcon name="telegram" width={21} />}
            sx={{ fontWeight: 500, minHeight: compact ? 42 : undefined }}
          >
            {labels.telegramApprove}
          </Button>
          <Alert severity="info">{labels.telegramWaiting}</Alert>
        </>
      ) : (
        <Button
          variant="outlined"
          size={compact ? 'medium' : 'large'}
          color="inherit"
          onClick={flow.startLogin}
          loading={flow.isStarting}
          disabled={flow.isMiniAppPending}
          startIcon={<OutlineIcon name="telegram" width={21} />}
          sx={{ fontWeight: 500, minHeight: compact ? 42 : undefined }}
        >
          {labels.telegramLogin}
        </Button>
      )}
    </Stack>
  );
}
