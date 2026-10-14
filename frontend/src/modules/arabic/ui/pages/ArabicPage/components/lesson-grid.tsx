import type { ArabicLabels } from '../../../labels';
import type { CoverTone } from 'src/shared/ui/learning-cover';
import type { ArabicLesson, ArabicCategory } from '../../../../domain';

import { Box, Card, Chip, Alert, Stack, Button, Typography } from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { learningCover } from 'src/shared/ui/learning-cover';

export const categoryTones: Record<ArabicCategory, CoverTone> = {
  alphabet: 'mint',
  quran_vocabulary: 'aqua',
  grammar: 'lavender',
  prayer_arabic: 'peach',
  sarf: 'blue',
  daily_phrases: 'rose',
  listening: 'amber',
};
/** Card cover/body composition from full Minimal overview/course/course-featured.tsx. */
export function LessonGrid({
  lessons,
  onSelect,
  labels,
  categoryTitle,
  categories,
}: {
  lessons: ArabicLesson[];
  onSelect: (id: number) => void;
  labels: ArabicLabels;
  categoryTitle?: string;
  categories: { key: string; title: string }[];
}) {
  if (!lessons.length) return <Alert severity="info">{labels.empty}</Alert>;
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(3,1fr)' },
        gap: 2.5,
      }}
    >
      {lessons.map((lesson) => {
        const preview = lesson.previewArabic.join('  ');
        return (
          <Card key={lesson.id} sx={{ display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 1, pb: 0 }}>
              <Box
                sx={(theme) => ({
                  position: 'relative',
                  overflow: 'hidden',
                  borderRadius: 2,
                  ...learningCover(theme, categoryTones[lesson.category]),
                  p: 2.5,
                  minHeight: 154,
                })}
              >
                <Box
                  aria-hidden
                  sx={{
                    position: 'absolute',
                    width: 190,
                    height: 190,
                    right: -40,
                    top: -45,
                    background:
                      'url(/assets/background/shape-circle-3.svg) center/contain no-repeat',
                    opacity: 0.07,
                  }}
                />
                <Stack
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                  spacing={1}
                  sx={{ position: 'relative' }}
                >
                  <Typography variant="overline">
                    {categoryTitle ??
                      categories.find((value) => value.key === lesson.category)?.title ??
                      labels[lesson.category]}
                  </Typography>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>
                    {String(lesson.order).padStart(2, '0')}
                  </Typography>
                </Stack>
                <Typography
                  lang={preview ? 'ar' : undefined}
                  dir={preview ? 'rtl' : undefined}
                  sx={{
                    fontFamily: preview ? 'Amiri,serif' : 'inherit',
                    fontSize: preview ? (lesson.category === 'alphabet' ? 44 : 28) : 24,
                    lineHeight: 1.6,
                    textAlign: 'center',
                    mt: 1,
                    minHeight: 76,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {preview || lesson.title}
                </Typography>
              </Box>
            </Box>
            <Stack spacing={2} sx={{ p: 3, flexGrow: 1 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
                <Chip
                  size="small"
                  variant="soft"
                  label={labels[lesson.status]}
                  color={
                    lesson.status === 'completed'
                      ? 'success'
                      : lesson.status === 'in_progress'
                        ? 'primary'
                        : 'default'
                  }
                />
                <Stack
                  direction="row"
                  spacing={0.5}
                  alignItems="center"
                  sx={{ color: 'text.secondary' }}
                >
                  <Iconify icon="solar:clock-circle-outline" width={15} />
                  <Typography variant="caption">
                    {lesson.estimatedMinutes} {labels.minutes}
                  </Typography>
                </Stack>
              </Stack>
              <Typography variant="h6">{lesson.title}</Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ lineHeight: 1.8, flexGrow: 1 }}
              >
                {lesson.summary}
              </Typography>
              <Button
                onClick={() => onSelect(lesson.id)}
                color="primary"
                endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
                sx={{ alignSelf: 'flex-start', px: 0 }}
              >
                {labels.open}
              </Button>
            </Stack>
          </Card>
        );
      })}
    </Box>
  );
}
