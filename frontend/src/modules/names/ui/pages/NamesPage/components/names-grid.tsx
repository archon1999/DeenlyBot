import type { NamesLabels } from '../../../labels';
import type { AllahName } from '../../../../domain';

import { Box, Card, Chip, Stack, Typography, CardActionArea } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

/** Adapted from full Minimal src/sections/job/job-item.tsx card hierarchy. */
export function NamesGrid({
  names,
  onSelect,
  labels,
}: {
  names: AllahName[];
  onSelect: (name: AllahName) => void;
  labels: NamesLabels;
}) {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(3,1fr)', xl: 'repeat(4,1fr)' },
        gap: 2.5,
      }}
    >
      {names.map((name) => (
        <Card
          key={name.id}
          sx={(theme) => ({
            transition: theme.transitions.create(['box-shadow', 'transform'], { duration: 160 }),
            '&:hover': { transform: 'translateY(-3px)' },
            '@media (prefers-reduced-motion: reduce)': {
              transition: 'none',
              '&:hover': { transform: 'none' },
            },
          })}
        >
          <CardActionArea
            onClick={() => onSelect(name)}
            sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
          >
            <Box sx={{ p: 2.5, pb: 0 }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
                <Box
                  sx={{
                    px: 1.25,
                    py: 0.5,
                    borderRadius: 1,
                    bgcolor: 'background.neutral',
                    typography: 'subtitle2',
                    color: 'text.secondary',
                  }}
                >
                  {String(name.order).padStart(2, '0')}
                </Box>
                <Chip
                  size="small"
                  variant="soft"
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
                  color={
                    name.isNext ? 'primary' : name.status === 'learned' ? 'success' : 'default'
                  }
                />
              </Stack>
              <Typography
                lang="ar"
                dir="rtl"
                sx={{
                  fontFamily: 'Amiri,serif',
                  fontSize: 42,
                  lineHeight: 1.9,
                  textAlign: 'center',
                  py: 2,
                  color: name.status === 'new' && !name.isNext ? 'text.primary' : 'primary.main',
                }}
              >
                {name.arabic}
              </Typography>
            </Box>
            <Stack
              spacing={1}
              sx={{ p: 2.5, pt: 1, flexGrow: 1, borderTop: '1px dashed', borderColor: 'divider' }}
            >
              <Typography variant="subtitle1">{name.transcription}</Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ flexGrow: 1, lineHeight: 1.7 }}
              >
                {name.meaning}
              </Typography>
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                sx={{ color: 'primary.main', pt: 1 }}
              >
                <Typography variant="caption" fontWeight="fontWeightSemiBold">
                  {labels.read}
                </Typography>
                <Iconify icon="eva:arrow-ios-forward-fill" width={14} />
              </Stack>
            </Stack>
          </CardActionArea>
        </Card>
      ))}
    </Box>
  );
}
