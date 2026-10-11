import { useEffect } from 'react';
import { useLocation } from 'react-router';

import { Box, Card, Chip, Stack, CardHeader, Typography } from '@mui/material';

import { QueryState } from 'src/shared/ui/query-state';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useAuthLabels } from '../../labels';
import { TelegramLink } from './components/telegram-link';
import { ProfileIdentity } from './components/profile-identity';
import { ProfileNameForm } from './components/profile-name-form';
import { useSession, useProfileQuery } from '../../../application';
import { AccountRegistration } from './components/account-registration';

export function ProfilePage() {
  const session = useSession();
  const query = useProfileQuery(session.authenticated);
  const labels = useAuthLabels();
  const profile = query.data;
  const { hash } = useLocation();
  useEffect(() => {
    if (profile && (hash === '#save-account' || hash === '#telegram-link'))
      document.getElementById(hash.slice(1))?.scrollIntoView({ block: 'center' });
  }, [hash, profile]);
  return (
    <DashboardContent maxWidth="xl">
      <Stack spacing={4}>
        <Box>
          <Typography variant="h3">{labels.profileTitle}</Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            {labels.profileIntro}
          </Typography>
        </Box>
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {profile && (
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: '300px minmax(0,1fr)' },
                gap: 3,
                alignItems: 'start',
              }}
            >
              <ProfileIdentity profile={profile} labels={labels} />
              <Stack spacing={3} sx={{ minWidth: 0 }}>
                {!profile.email && <AccountRegistration profile={profile} labels={labels} />}
                <ProfileNameForm key={profile.id} profile={profile} labels={labels} />
                <TelegramLink key={profile.id} profile={profile} labels={labels} />
                {profile.email && (
                  <Card>
                    <CardHeader
                      avatar={
                        <OutlineIcon name="email" width={24} sx={{ color: 'primary.main' }} />
                      }
                      title={labels.emailLinked}
                      subheader={profile.email}
                    />
                    <Box sx={{ p: 3, pt: 2 }}>
                      <Chip
                        label={labels.emailLinked}
                        variant="soft"
                        size="small"
                        color="success"
                        icon={<OutlineIcon name="check" width={16} />}
                      />
                    </Box>
                  </Card>
                )}
              </Stack>
            </Box>
          )}
        </QueryState>
      </Stack>
    </DashboardContent>
  );
}
