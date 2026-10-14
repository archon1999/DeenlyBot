import type { AllahName } from '../../../domain';

import { useState } from 'react';
import { useSearchParams } from 'react-router';

import { Box, Alert, Stack, TextField, Typography, InputAdornment } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { Iconify } from 'src/shared/ui/iconify';
import { QueryState } from 'src/shared/ui/query-state';
import { DashboardContent } from 'src/app/layouts/dashboard';
import { ReviewLink, ReviewSection } from 'src/shared/ui/review-navigation';

import { useNamesLabels } from '../../labels';
import { useNames } from '../../../application';
import { NameNext } from './components/name-next';
import { NameQuiz } from './components/name-quiz';
import { NamesGrid } from './components/names-grid';
import { NameMetrics } from './components/name-metrics';
import { NameLearning } from './components/name-learning';

export function NamesPage() {
  const query = useNames();
  const labels = useNamesLabels();
  const { language } = useLocale();
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState('');
  const selected =
    query.data?.results.find((name) => String(name.id) === params.get('name')) ?? null;
  const setSelected = (name: AllahName | null) => {
    const nextParams = new URLSearchParams(params);
    if (name) nextParams.set('name', String(name.id));
    else nextParams.delete('name');
    setParams(nextParams);
  };
  const data = query.data;
  const next = data?.results.find((name) => name.isNext);
  const names =
    data?.results.filter((name) =>
      `${name.arabic} ${name.transcription} ${name.meaning}`
        .toLowerCase()
        .includes(search.toLowerCase())
    ) ?? [];
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
              <NameMetrics data={data} labels={labels} />
              {next ? (
                <NameNext name={next} labels={labels} onSelect={setSelected} />
              ) : (
                <Alert severity="success">{labels.allDone}</Alert>
              )}
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={2}
                alignItems={{ sm: 'center' }}
                justifyContent="space-between"
              >
                <Typography variant="h5">
                  {labels.all}{' '}
                  <Typography component="span" color="text.disabled" variant="body2">
                    ({data.total})
                  </Typography>
                </Typography>
                <Stack
                  direction={{ xs: 'column', sm: 'row' }}
                  spacing={1.5}
                  alignItems={{ sm: 'center' }}
                >
                  <TextField
                    size="small"
                    label={labels.search}
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <Iconify icon="eva:search-fill" width={18} />
                          </InputAdornment>
                        ),
                      },
                    }}
                    sx={{ width: { xs: '100%', sm: 320 } }}
                  />
                  <ReviewLink targetId="names-review" />
                </Stack>
              </Stack>
              {names.length ? (
                <NamesGrid names={names} onSelect={setSelected} labels={labels} />
              ) : (
                <Alert severity="info">{labels.empty}</Alert>
              )}
              <ReviewSection id="names-review">
                <NameQuiz key={language} labels={labels} introduced={data.introducedCount} />
              </ReviewSection>
            </>
          )}
        </QueryState>
        <NameLearning
          key={selected?.id ?? 'closed'}
          name={selected}
          onClose={() => setSelected(null)}
          labels={labels}
        />
      </Stack>
    </DashboardContent>
  );
}
