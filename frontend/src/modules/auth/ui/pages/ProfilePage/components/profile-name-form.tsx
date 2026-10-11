import type { Profile } from '../../../../domain';
import type { AuthLabels } from '../../../labels';

import { Card, Alert, Stack, Button, TextField, CardHeader } from '@mui/material';

import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { AuthFormError } from '../../../../domain';
import { useUpdateProfile, useProfileNameDraft } from '../../../../application';

export function ProfileNameForm({ profile, labels }: { profile: Profile; labels: AuthLabels }) {
  const { name, setName } = useProfileNameDraft(profile.firstName);
  const mutation = useUpdateProfile();
  const fields = mutation.error instanceof AuthFormError ? mutation.error.fields : {};
  return (
    <Card>
      <CardHeader title={labels.personal} />
      <Stack
        component="form"
        spacing={2.5}
        sx={{ p: 3 }}
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate({ firstName: name }, { onSuccess: (data) => setName(data.firstName) });
        }}
      >
        <TextField
          required
          label={labels.firstName}
          value={name}
          onChange={(event) => {
            setName(event.target.value);
            mutation.reset();
          }}
          error={Boolean(fields.firstName)}
          helperText={fields.firstName}
          autoComplete="given-name"
          slotProps={{ htmlInput: { maxLength: 128 } }}
        />
        {mutation.error && <Alert severity="error">{mutation.error.message}</Alert>}
        {mutation.isSuccess && <Alert severity="success">{labels.saved}</Alert>}
        <Button
          type="submit"
          variant="contained"
          loading={mutation.isPending}
          startIcon={<OutlineIcon name="check" width={19} />}
          sx={{ alignSelf: 'flex-start', fontWeight: 500 }}
        >
          {labels.save}
        </Button>
      </Stack>
    </Card>
  );
}
