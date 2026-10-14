import type { ArabicCategory } from '../../../domain';

import { useState } from 'react';
import { useSearchParams } from 'react-router';

import { Box, Stack, Typography } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { QueryState } from 'src/shared/ui/query-state';
import { LearningTabs } from 'src/shared/ui/learning-tabs';
import { DashboardContent } from 'src/app/layouts/dashboard';

import { useArabicLabels } from '../../labels';
import { useArabic } from '../../../application';
import { LessonGrid } from './components/lesson-grid';
import { ArabicQuiz } from './components/arabic-quiz';
import { LessonReader } from './components/lesson-reader';
import { ArabicProgress } from './components/arabic-progress';

export function ArabicPage() {
  const query = useArabic();
  const labels = useArabicLabels();
  const { language } = useLocale();
  const [category, setCategory] = useState<ArabicCategory | 'all'>('all');
  const [params, setParams] = useSearchParams();
  const data = query.data;
  const rawId = params.get('lesson');
  const selectedId =
    rawId && Number.isSafeInteger(Number(rawId)) && Number(rawId) > 0 ? Number(rawId) : null;
  const setSelectedId = (id: number | null) => {
    const nextParams = new URLSearchParams(params);
    if (id !== null) nextParams.set('lesson', String(id));
    else nextParams.delete('lesson');
    setParams(nextParams);
  };
  return (
    <DashboardContent maxWidth="xl">
      <Stack spacing={4}>
        <Box>
          <Typography variant="h3">{labels.title}</Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            {labels.subtitle}
          </Typography>
        </Box>
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {data && (
            <>
              <ArabicProgress stats={data.stats} labels={labels} />
              <LearningTabs
                value={category}
                onChange={(value) => setCategory(value as ArabicCategory | 'all')}
                items={[{ key: 'all', title: labels.all }, ...data.categories]}
                label={labels.lessons}
              />
              {data.categories.find((value) => value.key === category)?.description && (
                <Typography variant="body2" color="text.secondary">
                  {data.categories.find((value) => value.key === category)?.description}
                </Typography>
              )}
              <LessonGrid
                lessons={data.lessons.filter(
                  (lesson) => category === 'all' || lesson.category === category
                )}
                onSelect={setSelectedId}
                labels={labels}
                categoryTitle={data.categories.find((value) => value.key === category)?.title}
                categories={data.categories}
              />
              <ArabicQuiz
                key={language}
                labels={labels}
                introduced={data.stats.introducedItems}
                audioCount={data.stats.audioCount}
              />
            </>
          )}
        </QueryState>
        <LessonReader
          key={selectedId ?? 'closed'}
          id={selectedId}
          onClose={() => setSelectedId(null)}
          labels={labels}
        />
      </Stack>
    </DashboardContent>
  );
}
