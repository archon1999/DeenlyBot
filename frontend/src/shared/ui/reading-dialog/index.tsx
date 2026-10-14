import type { ReactNode } from 'react';

import { useId } from 'react';

import {
  Box,
  Stack,
  Dialog,
  IconButton,
  Typography,
  DialogTitle,
  DialogActions,
  DialogContent,
} from '@mui/material';

import { OutlineIcon } from 'src/shared/ui/outline-icon';

type Props = {
  open: boolean;
  onClose: () => void;
  title: string;
  closeLabel: string;
  eyebrow?: ReactNode;
  children: ReactNode;
  actions?: ReactNode;
};

/** One reading surface: fixed title and actions, with only the text column scrolling. */
export function ReadingDialog({
  open,
  onClose,
  title,
  closeLabel,
  eyebrow,
  children,
  actions,
}: Props) {
  const titleId = useId();
  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="md"
      aria-labelledby={titleId}
      slotProps={{
        paper: {
          sx: {
            m: { xs: 0, sm: 3 },
            width: { xs: '100%', sm: 'calc(100% - 48px)' },
            maxWidth: { xs: '100%', sm: 920 },
            height: { xs: '100dvh', sm: 'auto' },
            maxHeight: { xs: '100dvh', sm: 'calc(100dvh - 48px)' },
            borderRadius: { xs: 0, sm: 3 },
          },
        },
      }}
    >
      <DialogTitle
        id={`${titleId}-header`}
        component="div"
        sx={{ px: { xs: 2.5, sm: 4 }, py: 2.5, flexShrink: 0 }}
      >
        <Stack direction="row" spacing={2} alignItems="flex-start" justifyContent="space-between">
          <Box sx={{ minWidth: 0 }}>
            {eyebrow && (
              <Box sx={{ mb: 0.75, color: 'primary.main', typography: 'caption' }}>{eyebrow}</Box>
            )}
            <Typography id={titleId} component="h2" variant="h5" sx={{ lineHeight: 1.45 }}>
              {title}
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
            aria-label={closeLabel}
            sx={{ width: 44, height: 44, flexShrink: 0, bgcolor: 'background.neutral' }}
          >
            <OutlineIcon name="close" />
          </IconButton>
        </Stack>
      </DialogTitle>
      <DialogContent
        sx={{ px: { xs: 2.5, sm: 4 }, pb: 4, minHeight: 0, overscrollBehavior: 'contain' }}
      >
        <Box sx={{ maxWidth: 720, mx: 'auto', pt: 1 }}>{children}</Box>
      </DialogContent>
      {actions && (
        <DialogActions
          sx={{
            px: { xs: 2.5, sm: 4 },
            pt: 2,
            pb: 'max(16px, env(safe-area-inset-bottom))',
            flexShrink: 0,
            flexWrap: 'wrap',
            gap: 1,
            bgcolor: 'background.neutral',
            '& > :not(style) ~ :not(style)': { ml: 0 },
          }}
        >
          {actions}
        </DialogActions>
      )}
    </Dialog>
  );
}
