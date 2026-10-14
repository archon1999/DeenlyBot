import type { BoxProps } from '@mui/material/Box';

import { Box } from '@mui/material';

/** The pointed arch echoes the Deenly mark without using sacred text as decoration. */
export function DeenlyArch({ sx, ...props }: BoxProps) {
  return (
    <Box
      aria-hidden
      sx={[{ pointerEvents: 'none', color: 'primary.main' }, ...(Array.isArray(sx) ? sx : [sx])]}
      {...props}
    >
      <svg viewBox="0 0 240 300" width="100%" height="100%" fill="none" focusable="false">
        <path
          d="M20 290V142C20 80 80 48 120 12c40 36 100 68 100 130v148"
          fill="currentColor"
          fillOpacity=".04"
          stroke="currentColor"
          strokeOpacity=".18"
        />
        <path
          d="M42 290V148c0-48 45-76 78-106 33 30 78 58 78 106v142"
          stroke="currentColor"
          strokeOpacity=".23"
        />
        <path
          d="M64 290V154c0-35 30-57 56-82 26 25 56 47 56 82v136"
          stroke="currentColor"
          strokeOpacity=".12"
        />
      </svg>
    </Box>
  );
}
