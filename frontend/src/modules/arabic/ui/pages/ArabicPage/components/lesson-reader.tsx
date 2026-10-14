import type { ArabicLabels } from '../../../labels';

import { Box, Card, Chip, Alert, Stack, Button, Divider, Typography } from '@mui/material';

import { RouterLink } from 'src/app/routes/components';
import { QueryState } from 'src/shared/ui/query-state';
import { AudioPlayer } from 'src/shared/ui/audio-player';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { ReadingDialog } from 'src/shared/ui/reading-dialog';
import { ContentSource } from 'src/shared/ui/content-source';
import { ReadingControls, useReadingPreferences } from 'src/shared/ui/reading-controls';

import {
  useArabic,
  useArabicLesson,
  useStartArabicLesson,
  useCompleteArabicLesson,
} from '../../../../application';

/** Reading column adapted from full Minimal blog/view/post-details-view.tsx. */
export function LessonReader({
  id,
  onClose,
  labels,
}: {
  id: number | null;
  onClose: () => void;
  labels: ArabicLabels;
}) {
  const query = useArabicLesson(id);
  const overview = useArabic();
  const start = useStartArabicLesson();
  const complete = useCompleteArabicLesson();
  const lesson = query.data;
  const preferences = useReadingPreferences(40);
  const close = () => {
    start.reset();
    complete.reset();
    onClose();
  };
  return (
    <ReadingDialog
      open={id !== null}
      onClose={close}
      title={lesson?.title ?? labels.lessons}
      closeLabel={labels.close}
      actions={
        <>
          <Button onClick={close} color="inherit">
            {labels.close}
          </Button>
          {lesson?.status === 'new' && (
            <Button
              variant="contained"
              loading={start.isPending}
              onClick={() => start.mutate(lesson.id)}
              endIcon={<OutlineIcon name="arrow-right" width={18} />}
            >
              {labels.start}
            </Button>
          )}
          {lesson?.status === 'in_progress' && (
            <Button
              variant="contained"
              loading={complete.isPending}
              onClick={() => complete.mutate(lesson.id)}
              startIcon={<OutlineIcon name="check" width={18} />}
            >
              {labels.complete}
            </Button>
          )}
        </>
      }
    >
      <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
        {id !== null && lesson && (
          <Stack spacing={3.5} sx={{ maxWidth: 720, mx: 'auto' }}>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip
                size="small"
                variant="soft"
                label={
                  overview.data?.categories.find((value) => value.key === lesson.category)?.title ??
                  labels[lesson.category]
                }
                color="primary"
              />
              <Chip
                size="small"
                variant="soft"
                label={labels[lesson.status]}
                color={lesson.status === 'completed' ? 'success' : 'default'}
              />
            </Stack>
            <Typography sx={{ whiteSpace: 'pre-line', lineHeight: 1.95, fontSize: 17 }}>
              {lesson.explanation}
            </Typography>
            <Divider sx={{ borderStyle: 'dashed' }} />
            <ReadingControls {...preferences} />
            <Typography variant="h6">{labels.items}</Typography>
            {lesson.items.map((item) => (
              <Card
                key={item.id}
                sx={{ p: { xs: 2.5, sm: 3 }, bgcolor: 'background.neutral', boxShadow: 'none' }}
              >
                <Stack spacing={2}>
                  <Typography
                    lang="ar"
                    dir="rtl"
                    sx={{
                      fontFamily: 'Amiri,serif',
                      fontSize: preferences.fontSize,
                      lineHeight: 1.9,
                      textAlign: 'center',
                      color: 'primary.main',
                    }}
                  >
                    {item.arabicText}
                  </Typography>
                  {preferences.transcription && item.transcription && (
                    <Typography textAlign="center" color="text.secondary">
                      {item.transcription}
                    </Typography>
                  )}
                  <Typography variant="h6" textAlign="center">
                    {item.meaning}
                  </Typography>
                  <AudioPlayer tracks={item.audioTracks ?? []} unavailable />
                  {item.quranReference && (
                    <Button
                      component={RouterLink}
                      href={`/library?reference=${encodeURIComponent(item.quranReference)}${item.quranPassage ? `&kind=${item.quranPassage.kind}&item=${item.quranPassage.id}` : ''}`}
                      onClick={close}
                      startIcon={<OutlineIcon name="library" width={18} />}
                    >
                      {labels.openReference} · {item.quranReference}
                    </Button>
                  )}
                  {item.explanation && (
                    <Box sx={{ pt: 2, mt: 1, borderTop: '1px dashed', borderColor: 'divider' }}>
                      <Typography sx={{ whiteSpace: 'pre-line', lineHeight: 1.9 }}>
                        {item.explanation}
                      </Typography>
                    </Box>
                  )}
                </Stack>
              </Card>
            ))}
            {(start.error || complete.error) && (
              <Alert severity="error">{(start.error || complete.error)?.message}</Alert>
            )}
            <ContentSource source={lesson.provenance} />
          </Stack>
        )}
      </QueryState>
    </ReadingDialog>
  );
}
