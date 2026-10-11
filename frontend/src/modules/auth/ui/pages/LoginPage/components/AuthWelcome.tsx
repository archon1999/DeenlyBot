import type { AuthLabels } from '../../../labels';

import { varAlpha } from 'minimal-shared/utils';

import { Box, Stack, Typography } from '@mui/material';

import { Logo } from 'src/shared/ui/logo';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

/** The same quiet arch/book artwork is used on both auth layouts. */
export function AuthIllustration({ maxHeight = 'min(23dvh, 180px)' }: { maxHeight?: string }) {
  return (
    <svg viewBox="0 0 420 250" width="100%" aria-hidden="true" fill="none" style={{ maxHeight }}>
      <ellipse cx="210" cy="220" rx="125" ry="13" fill="currentColor" opacity=".07" />
      <path
        d="M94 207V111c0-38 40-52 116-96 76 44 116 58 116 96v96"
        fill="currentColor"
        opacity=".045"
      />
      <path
        d="M120 207v-86c0-31 30-42 90-78 60 36 90 47 90 78v86"
        stroke="currentColor"
        strokeWidth="1.5"
        opacity=".25"
      />
      <path
        d="M145 207v-75c0-24 23-32 65-59 42 27 65 35 65 59v75"
        stroke="currentColor"
        strokeWidth="1.5"
        opacity=".15"
      />
      <path
        d="M138 171c24-8 48-3 72 11 24-14 48-19 72-11v42c-24-8-48-3-72 11-24-14-48-19-72-11Z"
        fill="var(--palette-background-paper)"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M210 182v42m-54-37c13-1 25 2 37 7m-37 7c13-1 25 2 37 7m71-21c-13-1-25 2-37 7m37 7c-13-1-25 2-37 7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity=".55"
      />
      <path
        d="M232 100a16 16 0 0 1-20-20 17 17 0 1 0 20 20Z"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="m63 114 4-9 4 9 9 4-9 4-4 9-4-9-9-4Zm285 27 3-7 3 7 7 3-7 3-3 7-3-7-7-3Z"
        fill="currentColor"
        opacity=".35"
      />
    </svg>
  );
}

export function AuthWelcome({ labels }: { labels: AuthLabels }) {
  return (
    <Box
      sx={(theme) => ({
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        minWidth: 0,
        height: '100dvh',
        p: { md: 3, lg: 4 },
        bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.035),
        ...theme.applyStyles('dark', {
          bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.06),
        }),
      })}
    >
      <Logo isSingle={false} sx={{ alignSelf: 'flex-start' }} />
      <Stack
        spacing={2.5}
        sx={{ flex: 1, minHeight: 0, justifyContent: 'center', maxWidth: 480, mx: 'auto' }}
      >
        <Box sx={{ color: 'primary.main', width: 1 }}>
          <AuthIllustration />
        </Box>
        <Box>
          <Typography variant="h3" sx={{ fontWeight: 500, lineHeight: 1.2, mb: 2 }}>
            {labels.heroTitle}
          </Typography>
          <Typography color="text.secondary" sx={{ lineHeight: 1.85 }}>
            {labels.heroBody}
          </Typography>
        </Box>
        <Stack spacing={1.5}>
          {(
            [
              { icon: 'names', text: labels.heroNames },
              { icon: 'arabic', text: labels.heroArabic },
              { icon: 'library', text: labels.heroLibrary },
            ] as const
          ).map((feature) => (
            <Stack key={feature.icon} direction="row" alignItems="center" spacing={1.5}>
              <Box
                sx={{
                  display: 'flex',
                  p: 1,
                  borderRadius: 1.25,
                  bgcolor: 'background.paper',
                  color: 'primary.main',
                }}
              >
                <OutlineIcon name={feature.icon} width={22} />
              </Box>
              <Typography variant="body2" fontWeight={500}>
                {feature.text}
              </Typography>
            </Stack>
          ))}
        </Stack>
      </Stack>
    </Box>
  );
}
