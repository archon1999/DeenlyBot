import type { ArabicLabels } from '../../../labels';

import {
  Box,
  Card,
  Chip,
  Alert,
  Stack,
  Button,
  Dialog,
  Divider,
  Typography,
  DialogTitle,
  DialogActions,
  DialogContent,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { RouterLink } from 'src/app/routes/components';
import { QueryState } from 'src/shared/ui/query-state';
import { AudioPlayer } from 'src/shared/ui/audio-player';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

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
  const close = () => {
    start.reset();
    complete.reset();
    onClose();
  };
  return (
    <Dialog open={id !== null} onClose={close} fullWidth maxWidth="md">
      <DialogTitle sx={{ px: { xs: 3, sm: 4 }, pt: 3, pb: 2 }}>
        <Typography component="span" variant="h5">
          {lesson?.title ?? labels.lessons}
        </Typography>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 3, sm: 4 }, pb: 4 }}>
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {id !== null && lesson && (
            <Stack spacing={3.5} sx={{ maxWidth: 720, mx: 'auto' }}>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip
                  size="small"
                  variant="soft"
                  label={
                    overview.data?.categories.find((value) => value.key === lesson.category)
                      ?.title ?? labels[lesson.category]
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
              <Typography variant="h6">{labels.items}</Typography>
              {lesson.items.map((item) => (
                <Card key={item.id} sx={{ p: { xs: 3, sm: 4 }, bgcolor: 'background.neutral' }}>
                  <Stack spacing={2}>
                    <Typography
                      lang="ar"
                      dir="rtl"
                      sx={{
                        fontFamily: 'Amiri,serif',
                        fontSize: 42,
                        lineHeight: 1.9,
                        textAlign: 'center',
                        color: 'primary.main',
                      }}
                    >
                      {item.arabicText}
                    </Typography>
                    {item.transcription && (
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
            </Stack>
          )}
        </QueryState>
      </DialogContent>
      <DialogActions sx={{ p: 3, borderTop: 1, borderColor: 'divider', gap: 1 }}>
        <Button onClick={close} color="inherit">
          {labels.close}
        </Button>
        {lesson?.status === 'new' && (
          <Button
            variant="contained"
            loading={start.isPending}
            onClick={() => start.mutate(lesson.id)}
            endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={18} />}
          >
            {labels.start}
          </Button>
        )}
        {lesson?.status === 'in_progress' && (
          <Button
            variant="contained"
            loading={complete.isPending}
            onClick={() => complete.mutate(lesson.id)}
            startIcon={<Iconify icon="solar:check-circle-bold" width={18} />}
          >
            {labels.complete}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
