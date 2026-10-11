import type { LibraryLabels } from '../../../labels';
import type { LibraryItem } from '../../../../domain';

import { Box, Card, Chip, Stack, Button, Tooltip, IconButton, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

/** Adapted from full Minimal src/sections/blog/post-item-horizontal.tsx. */
export function LibraryGrid({
  items,
  onRead,
  onSave,
  busyKey,
  labels,
}: {
  items: LibraryItem[];
  onRead: (item: LibraryItem) => void;
  onSave: (item: LibraryItem) => void;
  busyKey: string | null;
  labels: LibraryLabels;
}) {
  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 2.5 }}>
      {items.map((item) => (
        <Card
          key={`${item.kind}-${item.id}`}
          sx={{ display: 'flex', flexDirection: { xs: 'column-reverse', sm: 'row' } }}
        >
          <Stack spacing={2} sx={{ p: 3, flexGrow: 1, minWidth: 0 }}>
            <Stack direction="row" justifyContent="space-between" spacing={1} alignItems="center">
              <Chip
                size="small"
                variant="soft"
                color={item.kind === 'dua' ? 'info' : 'primary'}
                label={labels[item.kind]}
              />
              {item.reference && (
                <Typography variant="caption" color="text.disabled">
                  {item.reference}
                </Typography>
              )}
            </Stack>
            <Typography variant="h6" sx={{ lineHeight: 1.5 }}>
              {item.title}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                lineHeight: 1.85,
                flexGrow: 1,
                overflow: 'hidden',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {item.translation}
            </Typography>
            <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Button
                  onClick={() => onRead(item)}
                  endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
                  sx={{ px: 0 }}
                >
                  {labels.read}
                </Button>
                {item.isStudied && (
                  <Tooltip title={labels.studied}>
                    <Box
                      component="span"
                      aria-label={labels.studied}
                      sx={{ display: 'inline-flex', color: 'success.main' }}
                    >
                      <Iconify icon="solar:check-circle-bold" width={18} />
                    </Box>
                  </Tooltip>
                )}
              </Stack>
              <Tooltip title={item.isFavorite ? labels.remove : labels.save}>
                <IconButton
                  aria-label={item.isFavorite ? labels.remove : labels.save}
                  color={item.isFavorite ? 'primary' : 'default'}
                  loading={busyKey === `${item.kind}:${item.id}`}
                  onClick={() => onSave(item)}
                >
                  <Iconify
                    icon={item.isFavorite ? 'solar:heart-bold' : 'solar:heart-outline'}
                    width={21}
                  />
                </IconButton>
              </Tooltip>
            </Stack>
          </Stack>
          <Box
            sx={{
              p: 1,
              width: { xs: '100%', sm: 182 },
              flexShrink: 0,
              minHeight: { xs: 138, sm: 240 },
            }}
          >
            <Box
              sx={(theme) => ({
                height: '100%',
                position: 'relative',
                overflow: 'hidden',
                borderRadius: 2,
                bgcolor: 'primary.lighter',
                p: 2,
                display: 'flex',
                alignItems: 'center',
                ...theme.applyStyles('dark', { bgcolor: 'primary.darker' }),
              })}
            >
              <Box
                aria-hidden
                sx={{
                  position: 'absolute',
                  width: 210,
                  height: 210,
                  right: -40,
                  bottom: -80,
                  background: 'url(/assets/background/shape-circle-3.svg) center/contain no-repeat',
                  opacity: 0.06,
                }}
              />
              <Typography
                lang="ar"
                dir="rtl"
                sx={{
                  position: 'relative',
                  width: 1,
                  fontFamily: 'Amiri,serif',
                  fontSize: 26,
                  lineHeight: 1.95,
                  textAlign: 'center',
                  color: 'primary.main',
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: 'vertical',
                }}
              >
                {item.arabicText}
              </Typography>
            </Box>
          </Box>
        </Card>
      ))}
    </Box>
  );
}
