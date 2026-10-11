import type { LinkProps } from '@mui/material/Link';

import { Link, Typography } from '@mui/material';

import { RouterLink } from 'src/app/routes/components';

import { ARCH_D_PATH } from './arch-d-path';

export type LogoProps = LinkProps & { isSingle?: boolean; disabled?: boolean };
export function Logo({ isSingle = true, disabled, sx, href = '/', ...other }: LogoProps) {
  return (
    <Link
      component={RouterLink}
      href={href}
      aria-label="Deenly"
      underline="none"
      color="primary.main"
      sx={[
        (theme) => ({
          display: 'inline-flex',
          alignItems: 'center',
          gap: 1.3,
          flexShrink: 0,
          color: '#087F6F',
          ...theme.applyStyles('dark', { color: '#67D0B6' }),
          ...(disabled && { pointerEvents: 'none' }),
        }),
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
      {...other}
    >
      <svg width="38" height="38" viewBox="0 0 40 40" fill="none" aria-hidden="true">
        <path d={ARCH_D_PATH} fill="currentColor" fillRule="evenodd" clipRule="evenodd" />
      </svg>
      {!isSingle && (
        <Typography
          variant="h5"
          color="text.primary"
          sx={{
            fontFamily: '"Public Sans Variable", sans-serif',
            fontWeight: 700,
            letterSpacing: '-0.035em',
          }}
        >
          Deenly<span>.uz</span>
        </Typography>
      )}
    </Link>
  );
}
