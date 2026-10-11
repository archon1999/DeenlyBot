import type { LibraryLabels } from '../../../labels';
import type { LibraryWord, LibraryAnalysis } from '../../../../domain';

import { useState } from 'react';
import { varAlpha } from 'minimal-shared/utils';

import { Box, Card, Alert, Stack, Button, Typography } from '@mui/material';

export function LibraryAnalysisView({
  analysis,
  labels,
}: {
  analysis: LibraryAnalysis | null;
  labels: LibraryLabels;
}) {
  const [selected, setSelected] = useState<{ verse: string; word: LibraryWord } | null>(null);
  if (!analysis) return <Alert severity="info">{labels.analysisEmpty}</Alert>;
  return (
    <Stack spacing={3}>
      {[
        { title: labels.summary, text: analysis.summary },
        { title: labels.context, text: analysis.context },
        { title: labels.explanation, text: analysis.explanation },
      ]
        .filter((block) => block.text)
        .map((block) => (
          <Box key={block.title}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              {block.title}
            </Typography>
            <Typography color="text.secondary" sx={{ whiteSpace: 'pre-line', lineHeight: 1.9 }}>
              {block.text}
            </Typography>
          </Box>
        ))}
      <Typography variant="body2" color="text.secondary">
        {labels.wordHint}
      </Typography>
      {analysis.verses.map((verse) => (
        <Card key={verse.key} sx={{ p: { xs: 2.5, sm: 3 } }}>
          <Stack spacing={2}>
            <Typography variant="caption" color="text.secondary">
              {verse.key}
            </Typography>
            <Typography
              lang="ar"
              dir="rtl"
              sx={{ fontFamily: 'Amiri,serif', fontSize: 30, lineHeight: 2, textAlign: 'right' }}
            >
              {verse.arabicText}
            </Typography>
            {verse.transcription && (
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                {verse.transcription}
              </Typography>
            )}
            {verse.translation && (
              <Typography sx={{ lineHeight: 1.9 }}>{verse.translation}</Typography>
            )}
            <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1} dir="rtl">
              {verse.words.map((word) => {
                const active = selected?.verse === verse.key && selected.word.id === word.id;
                return (
                  <Button
                    key={word.id}
                    aria-pressed={active}
                    onClick={() => setSelected(active ? null : { verse: verse.key, word })}
                    lang="ar"
                    sx={(theme) => ({
                      px: 1.5,
                      py: 0.5,
                      fontFamily: 'Amiri,serif',
                      fontSize: 24,
                      lineHeight: 1.9,
                      fontWeight: 400,
                      bgcolor: active
                        ? varAlpha(theme.vars.palette.primary.mainChannel, 0.08)
                        : 'background.neutral',
                      color: active ? 'primary.main' : 'text.primary',
                    })}
                  >
                    {word.arabicText}
                  </Button>
                );
              })}
            </Stack>
            {selected?.verse === verse.key && (
              <Box
                role="status"
                aria-live="polite"
                sx={{ p: 2, borderRadius: 1.5, bgcolor: 'background.neutral' }}
              >
                <Stack spacing={1}>
                  <Typography
                    lang="ar"
                    dir="rtl"
                    sx={{ fontFamily: 'Amiri,serif', fontSize: 30, textAlign: 'right' }}
                  >
                    {selected.word.arabicText}
                  </Typography>
                  {selected.word.transcription && (
                    <Typography variant="body2" color="text.secondary">
                      {selected.word.transcription}
                    </Typography>
                  )}
                  <Typography variant="subtitle1">{selected.word.meaning}</Typography>
                  {selected.word.root && (
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Typography variant="caption" color="text.secondary">
                        {labels.root}:
                      </Typography>
                      <Typography
                        lang="ar"
                        dir="rtl"
                        sx={{ fontFamily: 'Amiri,serif', fontSize: 24 }}
                      >
                        {selected.word.root}
                      </Typography>
                    </Stack>
                  )}
                  {selected.word.grammarNote && (
                    <Typography variant="body2" sx={{ lineHeight: 1.8 }}>
                      <Box component="span" sx={{ color: 'text.secondary' }}>
                        {labels.grammar}:{' '}
                      </Box>
                      {selected.word.grammarNote}
                    </Typography>
                  )}
                </Stack>
              </Box>
            )}
          </Stack>
        </Card>
      ))}
    </Stack>
  );
}
