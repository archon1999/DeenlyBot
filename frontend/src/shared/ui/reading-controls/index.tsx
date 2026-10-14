import { useState } from 'react';

import { Box, Stack, Button, Switch, Typography, FormControlLabel } from '@mui/material';

import { useLocale } from 'src/shared/i18n';

const copy = {
  uz: {
    size: 'Matn o‘lchami',
    smaller: 'Matnni kichraytirish',
    larger: 'Matnni kattalashtirish',
    transcription: 'Transkripsiya',
  },
  ru: {
    size: 'Размер текста',
    smaller: 'Уменьшить текст',
    larger: 'Увеличить текст',
    transcription: 'Транскрипция',
  },
  en: {
    size: 'Text size',
    smaller: 'Smaller text',
    larger: 'Larger text',
    transcription: 'Transcription',
  },
};

export function useReadingPreferences(initialSize = 36) {
  const [fontSize, setFontSize] = useState(initialSize);
  const [transcription, setTranscription] = useState(true);
  return { fontSize, setFontSize, transcription, setTranscription };
}

export function ReadingControls({
  fontSize,
  setFontSize,
  transcription,
  setTranscription,
}: ReturnType<typeof useReadingPreferences>) {
  const labels = copy[useLocale().language];
  return (
    <Stack
      direction="row"
      alignItems="center"
      justifyContent="space-between"
      useFlexGap
      flexWrap="wrap"
      spacing={1}
      sx={{ py: 1, px: 1.5, borderRadius: 2, bgcolor: 'background.neutral' }}
    >
      <Stack
        direction="row"
        spacing={0.5}
        alignItems="center"
        role="group"
        aria-label={labels.size}
      >
        <Button
          color="inherit"
          aria-label={labels.smaller}
          disabled={fontSize <= 24}
          onClick={() => setFontSize((size) => Math.max(24, size - 4))}
          sx={{ minWidth: 44, height: 44 }}
        >
          A−
        </Button>
        <Typography variant="caption" sx={{ minWidth: 24, textAlign: 'center' }}>
          {fontSize}
        </Typography>
        <Button
          color="inherit"
          aria-label={labels.larger}
          disabled={fontSize >= 56}
          onClick={() => setFontSize((size) => Math.min(56, size + 4))}
          sx={{ minWidth: 44, height: 44 }}
        >
          A+
        </Button>
      </Stack>
      <Box>
        <FormControlLabel
          sx={{ m: 0, '& .MuiFormControlLabel-label': { typography: 'body2' } }}
          control={
            <Switch
              size="small"
              checked={transcription}
              onChange={(_, value) => setTranscription(value)}
              sx={{ mx: 0.5 }}
            />
          }
          label={labels.transcription}
        />
      </Box>
    </Stack>
  );
}
