import type { Profile } from '../../../../domain';
import type { AuthLabels } from '../../../labels';

import { Link } from 'react-router';

import { Box, Card, Chip, Stack, Avatar, Button, Divider, Typography } from '@mui/material';

import { OutlineIcon } from 'src/shared/ui/outline-icon';

export function ProfileIdentity({ profile, labels }: { profile: Profile; labels: AuthLabels }) {
  const name = profile.isGuest
    ? labels.guest
    : profile.firstName || profile.username || profile.email;
  const kind = profile.isGuest
    ? labels.guest
    : profile.accountKind === 'telegram'
      ? labels.telegramAccount
      : labels.member;
  return (
    <Card sx={{ p: 3 }}>
      <Stack spacing={2.5} alignItems="center">
        <Avatar
          sx={{
            width: 72,
            height: 72,
            bgcolor: 'background.neutral',
            color: 'primary.main',
            fontSize: 26,
            fontWeight: 500,
          }}
        >
          {profile.isGuest ? <OutlineIcon name="guest" width={32} /> : name.charAt(0).toUpperCase()}
        </Avatar>
        <Box textAlign="center">
          <Typography variant="h5">{name}</Typography>
          {profile.username && (
            <Typography color="text.secondary" sx={{ mt: 0.5 }}>
              @{profile.username}
            </Typography>
          )}
        </Box>
        <Chip
          label={kind}
          variant="soft"
          size="small"
          color={profile.isGuest ? 'default' : 'primary'}
        />
        <Divider flexItem sx={{ borderStyle: 'dashed' }} />
        <Stack spacing={2} sx={{ width: 1 }}>
          <Stack direction="row" spacing={1.25} alignItems="center">
            <OutlineIcon name="email" width={20} sx={{ color: 'text.secondary' }} />
            <Typography variant="body2" sx={{ overflowWrap: 'anywhere' }}>
              {profile.email || labels.notSet}
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1.25} alignItems="center">
            <OutlineIcon name="settings" width={20} sx={{ color: 'text.secondary' }} />
            <Box>
              <Typography variant="caption" color="text.secondary">
                {labels.timezone}
              </Typography>
              <Typography variant="body2">{profile.timezone}</Typography>
            </Box>
          </Stack>
        </Stack>
        <Button
          component={Link}
          to="/settings"
          color="inherit"
          startIcon={<OutlineIcon name="settings" width={19} />}
          sx={{ alignSelf: 'stretch', fontWeight: 500 }}
        >
          {labels.settings}
        </Button>
      </Stack>
    </Card>
  );
}
