import type { Profile } from '../../../../domain';
import type { AuthLabels } from '../../../labels';

import {
  Box,
  Card,
  Chip,
  Alert,
  Stack,
  Button,
  CardHeader,
  Typography,
  CardContent,
} from '@mui/material';

import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { useTelegramLinkFlow } from '../../../../application';
import { VerificationCode } from '../../../shared/VerificationCode';

export function TelegramLink({ profile, labels }: { profile: Profile; labels: AuthLabels }) {
  const flow = useTelegramLinkFlow();
  return (
    <Card id="telegram-link">
      <CardHeader
        avatar={
          <Box
            sx={{
              display: 'flex',
              p: 1.25,
              borderRadius: 1.5,
              bgcolor: 'background.neutral',
              color: 'primary.main',
            }}
          >
            <OutlineIcon name="telegram" width={24} />
          </Box>
        }
        title={profile.telegramLinked ? labels.linked : labels.linkTitle}
        subheader={profile.telegramLinked ? labels.linkedBody : labels.linkBody}
      />
      <CardContent sx={{ pt: 3 }}>
        {profile.telegramLinked ? (
          <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap" useFlexGap>
            <Chip
              label={labels.linked}
              size="small"
              variant="soft"
              color="success"
              icon={<OutlineIcon name="check" width={16} />}
            />
            {profile.username && (
              <Typography variant="body2" color="text.secondary">
                @{profile.username}
              </Typography>
            )}
          </Stack>
        ) : (
          <Stack spacing={2}>
            {flow.error instanceof Error && <Alert severity="error">{flow.error.message}</Alert>}
            {flow.expired && <Alert severity="warning">{labels.linkExpired}</Alert>}
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
                  variant="contained"
                  startIcon={<OutlineIcon name="telegram" width={20} />}
                  sx={{ alignSelf: 'flex-start', fontWeight: 500 }}
                >
                  {labels.linkApprove}
                </Button>
                <Alert severity="info">{labels.linkWaiting}</Alert>
              </>
            ) : (
              <Button
                variant="outlined"
                onClick={flow.startApproval}
                loading={flow.isStarting}
                startIcon={<OutlineIcon name="link" width={20} />}
                sx={{ alignSelf: 'flex-start', fontWeight: 500 }}
              >
                {labels.linkAction}
              </Button>
            )}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}
