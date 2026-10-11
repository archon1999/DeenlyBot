import type { LibraryLabels } from '../../../labels';
import type { LibraryItem } from '../../../../domain';

import { useId, useState } from 'react';

import {
  Box,
  Chip,
  Alert,
  Stack,
  Button,
  Dialog,
  Switch,
  Divider,
  Typography,
  DialogTitle,
  DialogActions,
  DialogContent,
  FormControlLabel,
} from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { QueryState } from 'src/shared/ui/query-state';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { AudioPlayer } from 'src/shared/ui/audio-player';
import { LearningTabs } from 'src/shared/ui/learning-tabs';

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
  const [fontSize, setFontSize] = useState(36);
  const [transcription, setTranscription] = useState(true);
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
  return (
    <Dialog open={Boolean(item)} onClose={close} fullWidth maxWidth="md">
      <DialogTitle sx={{ px: { xs: 3, sm: 4 }, pt: 3, pb: 2 }}>
        <Stack spacing={1.5}>
          {current && (
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip size="small" variant="soft" color="primary" label={labels[current.kind]} />
              {current.reference && (
                <Typography variant="caption" color="text.secondary">
                  {current.reference}
                </Typography>
              )}
            </Stack>
          )}
          <Typography component="span" variant="h5" sx={{ lineHeight: 1.5 }}>
            {current?.title}
          </Typography>
        </Stack>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 3, sm: 4 }, pb: 4 }}>
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
                  <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.neutral' }}>
                    <Stack
                      direction={{ xs: 'column', sm: 'row' }}
                      alignItems={{ sm: 'center' }}
                      justifyContent="space-between"
                      spacing={1.5}
                    >
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {labels.size}
                        </Typography>
                        <Stack direction="row" alignItems="center" spacing={0.5}>
                          <Button
                            size="small"
                            aria-label={labels.smaller}
                            onClick={() => setFontSize((value) => Math.max(24, value - 4))}
                            disabled={fontSize <= 24}
                            sx={{ minWidth: 40 }}
                          >
                            A−
                          </Button>
                          <Typography
                            variant="subtitle2"
                            sx={{ minWidth: 30, textAlign: 'center' }}
                          >
                            {fontSize}
                          </Typography>
                          <Button
                            size="small"
                            aria-label={labels.larger}
                            onClick={() => setFontSize((value) => Math.min(56, value + 4))}
                            disabled={fontSize >= 56}
                            sx={{ minWidth: 40 }}
                          >
                            A+
                          </Button>
                        </Stack>
                      </Box>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={transcription}
                            onChange={(_, value) => setTranscription(value)}
                          />
                        }
                        label={labels.showTranscription}
                      />
                    </Stack>
                  </Box>
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
                      {labels.translation}
                    </Typography>
                    <Typography
                      sx={{ mt: 1.25, whiteSpace: 'pre-line', lineHeight: 1.95, fontSize: 18 }}
                    >
                      {current.translation}
                    </Typography>
                  </Box>
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
      </DialogContent>
      <DialogActions sx={{ p: 3, borderTop: 1, borderColor: 'divider', gap: 1, flexWrap: 'wrap' }}>
        <Button onClick={close} color="inherit">
          {labels.close}
        </Button>
        {current && (
          <Button
            variant="contained"
            color="primary"
            loading={study.isPending}
            disabled={current.isStudied}
            startIcon={<OutlineIcon name="check" width={18} />}
            onClick={() =>
              study.mutate({ kind: current.kind, id: current.id }, { onSuccess: onStudied })
            }
          >
            {current.isStudied ? labels.studyDone : labels.study}
          </Button>
        )}
        {current && (
          <Button
            variant="outlined"
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
        )}
      </DialogActions>
    </Dialog>
  );
}
