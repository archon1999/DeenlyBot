import type { AuthLabels } from '../labels';

import { Box, Stack, Typography } from '@mui/material';

export function VerificationCode({ code, labels }: { code: string; labels: AuthLabels }) {
  return (
    <Box sx={{ p: 2, borderRadius: 1.5, bgcolor: 'background.neutral' }}>
      <Stack spacing={1} aria-live="polite">
        <Typography variant="caption" color="text.secondary">
          {labels.verificationCode}
        </Typography>
        <Typography
          component="code"
          sx={{ fontFamily: 'monospace', letterSpacing: 3, fontSize: 24, fontWeight: 500 }}
        >
          {code}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.8 }}>
          {labels.verificationHint}
        </Typography>
      </Stack>
    </Box>
  );
}
