import type { NamesLabels } from '../../../labels';
import type { AllahName } from '../../../../domain';

import { Box, Chip, Alert, Stack, Button, Typography } from '@mui/material';

import { DeenlyArch } from 'src/shared/ui/deenly-arch';
import { AudioPlayer } from 'src/shared/ui/audio-player';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { ReadingDialog } from 'src/shared/ui/reading-dialog';
import { ContentSource } from 'src/shared/ui/content-source';
import { ReadingControls, useReadingPreferences } from 'src/shared/ui/reading-controls';

import { useConfirmName } from '../../../../application';

/** Reader hierarchy adapted from full Minimal blog/view/post-details-view.tsx. */
export function NameLearning({
  name,
  onClose,
  labels,
}: {
  name: AllahName | null;
  onClose: () => void;
  labels: NamesLabels;
}) {
  const mutation = useConfirmName();
  const preferences = useReadingPreferences(48);
  const confirmed = mutation.isSuccess && mutation.variables === name?.id;
  const close = () => {
    mutation.reset();
    onClose();
  };
  return (
    <ReadingDialog
      open={Boolean(name)}
      onClose={close}
      title={name?.transcription ?? ''}
      closeLabel={labels.close}
      eyebrow={name && <Chip size="small" variant="soft" label={name.order} />}
      actions={
        <>
          <Button onClick={close} color="inherit">
            {labels.close}
          </Button>
          {name?.isNext && !confirmed && (
            <Button
              variant="contained"
              loading={mutation.isPending}
              startIcon={<OutlineIcon name="check" width={18} />}
              onClick={() => mutation.mutate(name.id)}
            >
              {labels.confirm}
            </Button>
          )}
        </>
      }
    >
      {name && (
        <Stack spacing={3.5}>
          <ReadingControls {...preferences} />
          <Box
            sx={{
              py: 3,
              mt: 1,
              position: 'relative',
              overflow: 'hidden',
              borderRadius: 2.5,
              bgcolor: 'background.neutral',
              textAlign: 'center',
            }}
          >
            <DeenlyArch
              sx={{
                position: 'absolute',
                width: 180,
                height: 225,
                left: '50%',
                top: 4,
                transform: 'translateX(-50%)',
              }}
            />
            <Typography
              lang="ar"
              dir="rtl"
              sx={{
                fontFamily: 'Amiri,serif',
                fontSize: preferences.fontSize,
                position: 'relative',
                lineHeight: 1.8,
                color: 'primary.main',
              }}
            >
              {name.arabic}
            </Typography>
            {preferences.transcription && (
              <Typography color="text.secondary" sx={{ position: 'relative', mb: 1 }}>
                {name.transcription}
              </Typography>
            )}
            <Chip
              label={
                name.isNext
                  ? labels.next
                  : labels[
                      name.status === 'learned'
                        ? 'learned'
                        : name.status === 'learning'
                          ? 'learning'
                          : 'new'
                    ]
              }
              variant="soft"
              color={name.status === 'learned' ? 'success' : 'primary'}
              size="small"
            />
          </Box>
          <AudioPlayer tracks={name.audioTracks ?? []} unavailable />
          <Box>
            <Typography variant="overline" color="text.secondary">
              {labels.meaning}
            </Typography>
            <Typography variant="h5" sx={{ mt: 1, lineHeight: 1.5 }}>
              {name.meaning}
            </Typography>
          </Box>
          <Box>
            <Typography variant="overline" color="text.secondary">
              {labels.description}
            </Typography>
            <Typography sx={{ mt: 1, whiteSpace: 'pre-line', lineHeight: 1.95 }}>
              {name.description}
            </Typography>
          </Box>
          {mutation.error && <Alert severity="error">{mutation.error.message}</Alert>}
          <ContentSource source={name.provenance} />
          {confirmed && <Alert severity="success">{labels.confirmed}</Alert>}
        </Stack>
      )}
    </ReadingDialog>
  );
}
