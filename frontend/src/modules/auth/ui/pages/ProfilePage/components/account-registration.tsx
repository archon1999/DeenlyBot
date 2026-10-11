import type { Profile } from '../../../../domain';
import type { AuthLabels } from '../../../labels';

import { Card, Alert, Stack, CardHeader, CardContent } from '@mui/material';

import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { CredentialsForm } from '../../../shared/CredentialsForm';

export function AccountRegistration({ profile, labels }: { profile: Profile; labels: AuthLabels }) {
  return (
    <Card id="save-account">
      <CardHeader
        title={profile.isGuest ? labels.upgradeTitle : labels.emailTitle}
        subheader={profile.isGuest ? labels.upgradeBody : labels.emailBody}
      />
      <CardContent sx={{ pt: 3 }}>
        <Stack spacing={3}>
          <Alert severity="info" icon={<OutlineIcon name="guest" width={20} />}>
            {labels.upgradeBody}
          </Alert>
          <CredentialsForm
            mode="register"
            labels={labels}
            initialFirstName={profile.firstName}
            submitLabel={labels.saveAccount}
          />
        </Stack>
      </CardContent>
    </Card>
  );
}
