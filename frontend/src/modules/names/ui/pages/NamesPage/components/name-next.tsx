import type { NamesLabels } from '../../../labels';
import type { AllahName } from '../../../../domain';

import { Box, Card, Chip, Stack, Button, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { AudioPlayer } from 'src/shared/ui/audio-player';

/** Continuation composition from full Minimal overview/course/course-continue.tsx. */
export function NameNext({
  name,
  onSelect,
  labels,
}: {
  name: AllahName;
  onSelect: (name: AllahName) => void;
  labels: NamesLabels;
}) {
  return (
    <Card
      sx={{
        p: { xs: 3, md: 4 },
        bgcolor: 'background.neutral',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Stack
        direction={{ xs: 'column-reverse', sm: 'row' }}
        spacing={3}
        alignItems={{ sm: 'center' }}
        justifyContent="space-between"
      >
        <Stack spacing={2} alignItems="flex-start" sx={{ position: 'relative', minWidth: 0 }}>
          <Chip
            label={`${labels.next} · ${name.order}`}
            color="primary"
            variant="soft"
            size="small"
          />
          <Box>
            <Typography variant="h4">{name.transcription}</Typography>
            <Typography color="text.secondary" sx={{ mt: 1, lineHeight: 1.8 }}>
              {name.meaning}
            </Typography>
          </Box>
          <Button
            variant="contained"
            onClick={() => onSelect(name)}
            endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={18} />}
            sx={{ minHeight: 46, px: 3 }}
          >
            {labels.read}
          </Button>
        </Stack>
        <Box
          sx={{
            position: 'relative',
            flexShrink: 0,
            minWidth: { sm: 260 },
            textAlign: 'center',
            alignSelf: { xs: 'center', sm: 'auto' },
          }}
        >
          <Typography
            lang="ar"
            dir="rtl"
            sx={{
              fontFamily: 'Amiri,serif',
              fontSize: { xs: 52, md: 64 },
              lineHeight: 1.8,
              color: 'primary.main',
            }}
          >
            {name.arabic}
          </Typography>
        </Box>
      </Stack>
      {!!name.audioTracks?.length && (
        <Box sx={{ mt: 3 }}>
          <AudioPlayer tracks={name.audioTracks} />
        </Box>
      )}
    </Card>
  );
}
