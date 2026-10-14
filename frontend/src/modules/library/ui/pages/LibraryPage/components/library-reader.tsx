import type { LibraryLabels } from '../../../labels';
import type { LibraryItem } from '../../../../domain';

import { useId, useState } from 'react';

import { Box, Chip, Alert, Stack, Button, Divider, Typography } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { QueryState } from 'src/shared/ui/query-state';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { AudioPlayer } from 'src/shared/ui/audio-player';
import { LearningTabs } from 'src/shared/ui/learning-tabs';
import { ReadingDialog } from 'src/shared/ui/reading-dialog';
import { ContentSource, useMeaningLabel } from 'src/shared/ui/content-source';
import { ReadingControls, useReadingPreferences } from 'src/shared/ui/reading-controls';

import { LibraryQuiz } from './library-quiz';
import { LibraryAnalysisView } from './library-analysis';
import {
  useSaveFavorite,
  useLibraryDetail,
  useLibraryPractice,
  useStudyLibraryItem,
} from '../../../../application';

/** One reader for text, audio, analysis and deliberate study, without duplicate content. */
export function LibraryReader({
  item,
  onClose,
  onSaved,
  onStudied,
  labels,
}: {
  item: LibraryItem | null;
  onClose: () => void;
  onSaved: (saved: boolean) => void;
  onStudied: () => void;
  labels: LibraryLabels;
}) {
  const preferences = useReadingPreferences();
  const { fontSize, transcription } = preferences;
  const [tab, setTab] = useState('text');
  const id = useId();
  const { language } = useLocale();
  const detail = useLibraryDetail(item?.kind ?? 'ayah', item?.id ?? null);
  const practice = useLibraryPractice(item?.kind ?? 'ayah');
  const mutation = useSaveFavorite();
  const study = useStudyLibraryItem();
  const current =
    detail.data && item
      ? {
          ...detail.data,
          isFavorite: item.isFavorite,
          isStudied: item.isStudied || detail.data.isStudied,
        }
      : item;
  const close = () => {
    mutation.reset();
    study.reset();
    onClose();
  };
  const meaningLabel = useMeaningLabel(current?.provenance);
  return (
    <ReadingDialog
      open={Boolean(item)}
      onClose={close}
      title={current?.title ?? labels.title}
      closeLabel={labels.close}
      eyebrow={
        current && (
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip size="small" variant="soft" color="primary" label={labels[current.kind]} />
            {current.reference && (
              <Typography variant="caption" color="text.secondary">
                {current.reference}
              </Typography>
            )}
          </Stack>
        )
      }
      actions={
        current && (
          <>
            <Button
              variant="outlined"
              color="inherit"
              loading={mutation.isPending}
              startIcon={<OutlineIcon name="library" width={18} />}
              onClick={() =>
                mutation.mutate(
                  { kind: current.kind, id: current.id, saved: !current.isFavorite },
                  { onSuccess: (data) => onSaved(data.saved) }
                )
              }
            >
              {current.isFavorite ? labels.remove : labels.save}
            </Button>
            <Button
              variant="contained"
              loading={study.isPending}
              disabled={current.isStudied}
              startIcon={<OutlineIcon name="check" width={18} />}
              onClick={() =>
                study.mutate({ kind: current.kind, id: current.id }, { onSuccess: onStudied })
              }
            >
              {current.isStudied ? labels.studyDone : labels.study}
            </Button>
          </>
        )
      }
    >
      {current && (
        <Stack spacing={3} sx={{ maxWidth: 760, mx: 'auto', pt: 1 }}>
          <AudioPlayer tracks={current.audioTracks ?? []} unavailable={!detail.isPending} />
          <LearningTabs
            value={tab}
            onChange={setTab}
            label={current.title}
            items={[
              { key: 'text', title: labels.textTab },
              { key: 'analysis', title: labels.analysisTab },
              { key: 'practice', title: labels.practiceTab },
            ]}
          />
          <Box
            role="tabpanel"
            id={`${id}-${tab}`}
            aria-label={
              tab === 'text'
                ? labels.textTab
                : tab === 'analysis'
                  ? labels.analysisTab
                  : labels.practiceTab
            }
          >
            {tab === 'text' && (
              <Stack spacing={3.5}>
                <ReadingControls {...preferences} />
                <Typography
                  lang="ar"
                  dir="rtl"
                  sx={{
                    fontFamily: 'Amiri,serif',
                    fontSize,
                    lineHeight: 2.15,
                    textAlign: 'right',
                    whiteSpace: 'pre-line',
                    py: 2,
                  }}
                >
                  {current.arabicText}
                </Typography>
                <Divider sx={{ borderStyle: 'dashed' }} />
                {transcription && current.transcription && (
                  <Box>
                    <Typography variant="overline" color="text.secondary">
                      {labels.transcription}
                    </Typography>
                    <Typography
                      sx={{
                        mt: 1,
                        whiteSpace: 'pre-line',
                        lineHeight: 1.95,
                        color: 'text.secondary',
                      }}
                    >
                      {current.transcription}
                    </Typography>
                  </Box>
                )}
                <Box>
                  <Typography variant="overline" color="primary.main">
                    {meaningLabel}
                  </Typography>
                  <Typography
                    sx={{ mt: 1.25, whiteSpace: 'pre-line', lineHeight: 1.95, fontSize: 18 }}
                  >
                    {current.translation}
                  </Typography>
                </Box>
                <ContentSource source={current.provenance} />
              </Stack>
            )}
            {tab === 'analysis' && (
              <QueryState
                isPending={detail.isPending}
                error={detail.error}
                onRetry={() => detail.refetch()}
              >
                {detail.data && (
                  <LibraryAnalysisView analysis={detail.data.analysis} labels={labels} />
                )}
              </QueryState>
            )}
            {tab === 'practice' && (
              <Stack spacing={2}>
                <Typography variant="body2" color="text.secondary">
                  {labels.itemPracticeHint}
                </Typography>
                {!current.isStudied ? (
                  <Alert severity="info">{labels.studyBeforePractice}</Alert>
                ) : (
                  <QueryState
                    isPending={practice.isPending}
                    error={practice.error}
                    onRetry={() => practice.refetch()}
                  >
                    {practice.data && (
                      <LibraryQuiz
                        key={`${language}:${current.kind}:${current.id}`}
                        kind={current.kind}
                        itemId={current.id}
                        labels={labels}
                        introduced={practice.data.studiedCount}
                        audioCount={practice.data.audioCount}
                      />
                    )}
                  </QueryState>
                )}
              </Stack>
            )}
          </Box>
          {detail.error && tab !== 'analysis' && (
            <Alert severity="warning">{detail.error.message}</Alert>
          )}
          {mutation.error && <Alert severity="error">{mutation.error.message}</Alert>}
          <Typography variant="body2" color="text.secondary">
            {labels.studyHint}
          </Typography>
          {study.error && <Alert severity="error">{study.error.message}</Alert>}
        </Stack>
      )}
    </ReadingDialog>
  );
}
