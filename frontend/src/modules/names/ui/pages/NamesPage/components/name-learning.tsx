import type { NamesLabels } from '../../../labels';
import type { AllahName } from '../../../../domain';

import {
  Box,
  Chip,
  Alert,
  Stack,
  Button,
  Dialog,
  Typography,
  DialogTitle,
  DialogActions,
  DialogContent,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { AudioPlayer } from 'src/shared/ui/audio-player';

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
  const confirmed = mutation.isSuccess && mutation.variables === name?.id;
  const close = () => {
    mutation.reset();
    onClose();
  };
  return (
    <Dialog open={Boolean(name)} onClose={close} fullWidth maxWidth="sm">
      {name && (
        <>
          <DialogTitle sx={{ pb: 1 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
              <Typography variant="h5" component="span">
                {name.transcription}
              </Typography>
              <Chip size="small" variant="soft" label={name.order} />
            </Stack>
          </DialogTitle>
          <DialogContent sx={{ px: { xs: 3, sm: 4 }, pb: 4 }}>
            <Stack spacing={3.5}>
              <Box
                sx={{
                  py: 3,
                  mt: 1,
                  borderRadius: 2.5,
                  bgcolor: 'background.neutral',
                  textAlign: 'center',
                }}
              >
                <Typography
                  lang="ar"
                  dir="rtl"
                  sx={{
                    fontFamily: 'Amiri,serif',
                    fontSize: 58,
                    lineHeight: 1.8,
                    color: 'primary.main',
                  }}
                >
                  {name.arabic}
                </Typography>
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
              {confirmed && <Alert severity="success">{labels.confirmed}</Alert>}
            </Stack>
          </DialogContent>
          <DialogActions sx={{ p: 3, borderTop: 1, borderColor: 'divider', gap: 1 }}>
            <Button onClick={close} color="inherit">
              {labels.close}
            </Button>
            {name.isNext && !confirmed && (
              <Button
                variant="contained"
                loading={mutation.isPending}
                startIcon={<Iconify icon="solar:check-circle-bold" width={18} />}
                onClick={() => mutation.mutate(name.id)}
              >
                {labels.confirm}
              </Button>
            )}
          </DialogActions>
        </>
      )}
    </Dialog>
  );
}
