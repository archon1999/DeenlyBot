import type { LibraryItem, LibraryFilter } from '../../../domain';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router';

import {
  Box,
  Card,
  Alert,
  Stack,
  Button,
  TextField,
  Pagination,
  Typography,
  InputAdornment,
} from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { Iconify } from 'src/shared/ui/iconify';
import { QueryState } from 'src/shared/ui/query-state';
import { LearningTabs } from 'src/shared/ui/learning-tabs';
import { DashboardContent } from 'src/app/layouts/dashboard';
import { ReviewLink, ReviewSection } from 'src/shared/ui/review-navigation';

import { useLibraryLabels } from '../../labels';
import { LibraryGrid } from './components/library-grid';
import { LibraryQuiz } from './components/library-quiz';
import { LibraryReader } from './components/library-reader';
import { LibraryProgress } from './components/library-progress';
import {
  useLibrary,
  useSaveFavorite,
  useLibraryDetail,
  useLibraryPractice,
} from '../../../application';

export function LibraryPage() {
  const { language } = useLocale();
  const labels = useLibraryLabels();
  const [params, setParams] = useSearchParams();
  const reference = params.get('reference') ?? '';
  const linkedKind = ['ayah', 'surah', 'dua'].includes(params.get('kind') ?? '')
    ? (params.get('kind') as 'ayah' | 'surah' | 'dua')
    : 'ayah';
  const rawLinkedId = Number(params.get('item'));
  const linkedId = Number.isSafeInteger(rawLinkedId) && rawLinkedId > 0 ? rawLinkedId : null;
  const linkedDetail = useLibraryDetail(linkedKind, linkedId);
  const [kind, setKind] = useState<LibraryFilter>(linkedKind);
  const [page, setPage] = useState(1);
  const [input, setInput] = useState(reference);
  const [q, setQ] = useState(reference);
  const [selected, setSelected] = useState<LibraryItem | null>(null);
  useEffect(() => {
    if (linkedId && linkedDetail.data) setSelected(linkedDetail.data);
  }, [linkedId, linkedDetail.data]);
  const closeReader = () => {
    setSelected(null);
    if (params.has('item')) {
      const next = new URLSearchParams(params);
      next.delete('item');
      setParams(next, { replace: true });
    }
  };
  const query = useLibrary({ kind, page, q });
  const practice = useLibraryPractice(kind);
  const favorite = useSaveFavorite();
  const data = query.data;
  return (
    <DashboardContent maxWidth="xl">
      <Stack spacing={4}>
        <Box>
          <Typography variant="h3">{labels.title}</Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            {labels.subtitle}
          </Typography>
        </Box>
        <QueryState
          isPending={practice.isPending}
          error={practice.error}
          onRetry={() => practice.refetch()}
        >
          {practice.data && <LibraryProgress stats={practice.data} labels={labels} />}
        </QueryState>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1.5}
          alignItems={{ xs: 'stretch', sm: 'center' }}
        >
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <LearningTabs
              value={kind}
              label={labels.title}
              items={(['ayah', 'surah', 'dua', 'favorites'] as const).map((key) => ({
                key,
                title: labels[key],
              }))}
              onChange={(value) => {
                setKind(value as LibraryFilter);
                setPage(1);
              }}
            />
          </Box>
          {practice.data && <ReviewLink targetId="library-review" />}
        </Stack>
        <Card sx={{ p: 2.5 }}>
          <Stack
            component="form"
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.5}
            onSubmit={(event) => {
              event.preventDefault();
              setQ(input.trim());
              setPage(1);
            }}
          >
            <TextField
              fullWidth
              size="small"
              label={labels.search}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <Iconify icon="eva:search-fill" width={18} />
                    </InputAdornment>
                  ),
                },
              }}
            />
            <Button type="submit" variant="outlined">
              {labels.find}
            </Button>
          </Stack>
        </Card>
        {favorite.error && <Alert severity="error">{favorite.error.message}</Alert>}
        {linkedDetail.error && <Alert severity="warning">{linkedDetail.error.message}</Alert>}
        <QueryState isPending={query.isPending} error={query.error} onRetry={() => query.refetch()}>
          {data && (
            <>
              <Typography variant="body2" color="text.secondary">
                {data.count} {labels.items}
              </Typography>
              {data.results.length ? (
                <LibraryGrid
                  items={data.results}
                  labels={labels}
                  onRead={setSelected}
                  onSave={(item) => {
                    if (kind === 'favorites') setPage(1);
                    favorite.mutate({ kind: item.kind, id: item.id, saved: !item.isFavorite });
                  }}
                  busyKey={
                    favorite.isPending
                      ? `${favorite.variables?.kind}:${favorite.variables?.id}`
                      : null
                  }
                />
              ) : (
                <Alert severity="info">{q ? labels.noResults : labels.empty}</Alert>
              )}
              {data.pages > 1 && (
                <Stack alignItems="center">
                  <Pagination
                    count={data.pages}
                    page={page}
                    getItemAriaLabel={(type, itemPage, isCurrent) => {
                      if (type === 'page')
                        return `${labels.page} ${itemPage}${isCurrent ? `, ${labels.currentPage}` : ''}`;
                      if (type === 'first') return labels.firstPage;
                      if (type === 'last') return labels.lastPage;
                      if (type === 'next') return labels.nextPage;
                      return labels.previousPage;
                    }}
                    onChange={(_, value) => setPage(value)}
                    color="primary"
                    disabled={query.isFetching}
                  />
                </Stack>
              )}
            </>
          )}
        </QueryState>
        {practice.data && (
          <ReviewSection id="library-review">
            <LibraryQuiz
              key={`${language}:${kind}`}
              kind={kind}
              labels={labels}
              introduced={practice.data.studiedCount}
              audioCount={practice.data.audioCount}
            />
          </ReviewSection>
        )}
        <LibraryReader
          key={selected ? `${language}:${selected.kind}:${selected.id}` : 'closed'}
          item={selected}
          onClose={closeReader}
          labels={labels}
          onStudied={() =>
            setSelected((previous) => (previous ? { ...previous, isStudied: true } : null))
          }
          onSaved={(saved) => {
            if (kind === 'favorites') setPage(1);
            setSelected((previous) => (previous ? { ...previous, isFavorite: saved } : null));
          }}
        />
      </Stack>
    </DashboardContent>
  );
}
