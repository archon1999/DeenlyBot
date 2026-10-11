import type { ReactNode } from 'react';
import type { AudioTrack, PracticeMode } from 'src/shared/domain/audio';

import { useState } from 'react';

import {
  Box,
  Card,
  Alert,
  Stack,
  Button,
  Switch,
  CardHeader,
  Typography,
  CardContent,
  ToggleButton,
  LinearProgress,
  FormControlLabel,
  ToggleButtonGroup,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';
import { AudioPlayer } from 'src/shared/ui/audio-player';

export type PracticeQuizLabels = {
  quiz: string;
  quizHint: string;
  practice: string;
  review: string;
  again: string;
  quizLocked: string;
  noQuiz: string;
  correct: string;
  incorrect: string;
  answer: string;
};
export type PracticeQuestion = {
  prompt: string;
  title: string;
  options: { label: string }[];
  arabicPrompt: boolean;
  arabicOptions: boolean;
  audioTracks?: AudioTrack[];
};
export type PracticeResult = {
  isCorrect: boolean;
  correctOption: number;
  answerLabel: string;
  answerMeaning: string;
};

/** Shared presentation only: domain decisions and requests stay in each feature. */
export function PracticeQuiz({
  labels,
  introduced,
  question,
  result,
  creating,
  answering,
  noQuestion,
  error,
  onStart,
  onAnswer,
  icon,
  modeLabels,
  audioCount = 0,
  initialExtra = false,
}: {
  labels: PracticeQuizLabels;
  introduced: number;
  question?: PracticeQuestion | null;
  result?: PracticeResult;
  creating: boolean;
  answering: boolean;
  noQuestion: boolean;
  error?: Error | null;
  onStart: (extra: boolean, mode: PracticeMode) => void;
  onAnswer: (option: number) => void;
  icon: ReactNode;
  audioCount?: number;
  initialExtra?: boolean;
  modeLabels?: { text: string; listening: string; audioLocked: string; audioNoQuiz: string };
}) {
  const [extra, setExtra] = useState(initialExtra);
  const [selected, setSelected] = useState<number | null>(null);
  const [mode, setMode] = useState<PracticeMode>('text');
  const start = () => {
    setSelected(null);
    onStart(extra, mode);
  };
  return (
    <Card>
      <CardHeader
        avatar={
          <Box
            sx={{
              p: 1.25,
              borderRadius: 1.5,
              bgcolor: 'background.neutral',
              color: 'primary.main',
              display: 'flex',
            }}
          >
            {icon}
          </Box>
        }
        title={labels.quiz}
        subheader={labels.quizHint}
      />
      <CardContent sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={3}>
          {!question && modeLabels && (
            <ToggleButtonGroup
              value={mode}
              exclusive
              onChange={(_, value) => {
                if (value) setMode(value);
              }}
              disabled={creating}
              size="small"
              sx={{ alignSelf: 'flex-start' }}
            >
              <ToggleButton value="text">{modeLabels.text}</ToggleButton>
              <ToggleButton value="listening">{modeLabels.listening}</ToggleButton>
            </ToggleButtonGroup>
          )}
          {!question && (
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              alignItems={{ sm: 'center' }}
              justifyContent="space-between"
              spacing={2}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={extra}
                    disabled={creating}
                    onChange={(_, value) => setExtra(value)}
                  />
                }
                label={labels.practice}
              />
              <Button
                variant="contained"
                loading={creating}
                disabled={introduced < 4 || (mode === 'listening' && audioCount < 4)}
                onClick={start}
                endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
              >
                {labels.review}
              </Button>
            </Stack>
          )}
          {introduced < 4 && <Alert severity="info">{labels.quizLocked}</Alert>}
          {mode === 'listening' && introduced >= 4 && audioCount < 4 && modeLabels && (
            <Alert severity="info">{modeLabels.audioLocked}</Alert>
          )}
          {noQuestion && introduced >= 4 && (
            <Alert severity="info">
              {mode === 'listening' && modeLabels ? modeLabels.audioNoQuiz : labels.noQuiz}
            </Alert>
          )}
          {question && (
            <>
              <Box sx={{ p: { xs: 2, sm: 3 }, borderRadius: 2, bgcolor: 'background.neutral' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {question.title}
                </Typography>
                {!!question.audioTracks?.length && (
                  <Box sx={{ mt: 2 }}>
                    <AudioPlayer
                      key={question.audioTracks.map((track) => track.url).join('|')}
                      tracks={question.audioTracks}
                    />
                  </Box>
                )}
                <Typography
                  variant="h5"
                  lang={question.arabicPrompt ? 'ar' : undefined}
                  dir={question.arabicPrompt ? 'rtl' : 'ltr'}
                  sx={{
                    whiteSpace: 'pre-line',
                    overflowWrap: 'anywhere',
                    lineHeight: 1.9,
                    fontSize: question.arabicPrompt ? 32 : undefined,
                    fontFamily: question.arabicPrompt ? 'Amiri,serif' : undefined,
                  }}
                >
                  {question.prompt}
                </Typography>
              </Box>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                  gap: 1.5,
                }}
              >
                {question.options.map((option, index) => {
                  const correct = Boolean(result && index === result.correctOption);
                  const wrong = Boolean(result && !result.isCorrect && selected === index);
                  const active = selected === index;
                  return (
                    <Button
                      key={index}
                      variant="outlined"
                      color={correct ? 'success' : wrong ? 'error' : active ? 'primary' : 'inherit'}
                      disabled={creating || answering || Boolean(result)}
                      onClick={() => {
                        setSelected(index);
                        onAnswer(index);
                      }}
                      sx={(theme) => ({
                        p: 2,
                        minHeight: 80,
                        textAlign: 'left',
                        justifyContent: 'flex-start',
                        gap: 2,
                        fontSize: 18,
                        fontWeight: 500,
                        borderColor: correct
                          ? 'success.main'
                          : wrong
                            ? 'error.main'
                            : active
                              ? 'primary.main'
                              : 'divider',
                        bgcolor: correct
                          ? 'success.lighter'
                          : wrong
                            ? 'error.lighter'
                            : active
                              ? 'primary.lighter'
                              : 'transparent',
                        '&.Mui-disabled': {
                          color: correct ? 'success.dark' : wrong ? 'error.dark' : 'text.secondary',
                          borderColor: correct ? 'success.main' : wrong ? 'error.main' : 'divider',
                        },
                        ...theme.applyStyles('dark', {
                          bgcolor: correct
                            ? 'success.darker'
                            : wrong
                              ? 'error.darker'
                              : active
                                ? 'primary.darker'
                                : 'transparent',
                          '&.Mui-disabled': {
                            color: correct
                              ? 'success.light'
                              : wrong
                                ? 'error.light'
                                : 'text.secondary',
                            borderColor: correct
                              ? 'success.main'
                              : wrong
                                ? 'error.main'
                                : 'divider',
                          },
                        }),
                      })}
                    >
                      <Box
                        component="span"
                        sx={{
                          width: 30,
                          height: 30,
                          borderRadius: 1,
                          flexShrink: 0,
                          bgcolor: 'action.hover',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          typography: 'subtitle2',
                        }}
                      >
                        {correct ? (
                          <Iconify icon="solar:check-circle-bold" width={19} />
                        ) : (
                          String.fromCharCode(65 + index)
                        )}
                      </Box>
                      <Box
                        component="span"
                        lang={question.arabicOptions ? 'ar' : undefined}
                        dir={question.arabicOptions ? 'rtl' : 'ltr'}
                        sx={{
                          whiteSpace: 'pre-line',
                          overflowWrap: 'anywhere',
                          minWidth: 0,
                          width: 1,
                          textAlign: question.arabicOptions ? 'right' : 'left',
                          fontSize: question.arabicOptions ? 28 : undefined,
                          fontFamily: question.arabicOptions ? 'Amiri,serif' : undefined,
                          lineHeight: 1.9,
                        }}
                      >
                        {option.label}
                      </Box>
                    </Button>
                  );
                })}
              </Box>
              {answering && <LinearProgress />}
              {result && (
                <>
                  <Alert severity={result.isCorrect ? 'success' : 'warning'} aria-live="polite">
                    <Typography variant="subtitle2">
                      {result.isCorrect ? labels.correct : labels.incorrect}
                    </Typography>
                    <Typography variant="body2">{labels.answer}:</Typography>
                    <Typography
                      lang={question.arabicOptions ? 'ar' : undefined}
                      dir={question.arabicOptions ? 'rtl' : 'ltr'}
                      sx={{
                        whiteSpace: 'pre-line',
                        overflowWrap: 'anywhere',
                        fontFamily: question.arabicOptions ? 'Amiri,serif' : undefined,
                        fontSize: question.arabicOptions ? 26 : undefined,
                        lineHeight: 1.9,
                      }}
                    >
                      {result.answerLabel}
                    </Typography>
                    {result.answerMeaning !== result.answerLabel && (
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                        {result.answerMeaning}
                      </Typography>
                    )}
                  </Alert>
                  <Button
                    variant="contained"
                    loading={creating}
                    onClick={start}
                    startIcon={<Iconify icon="solar:restart-bold" width={18} />}
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    {labels.again}
                  </Button>
                </>
              )}
            </>
          )}
          {error && <Alert severity="error">{error.message}</Alert>}
        </Stack>
      </CardContent>
    </Card>
  );
}
