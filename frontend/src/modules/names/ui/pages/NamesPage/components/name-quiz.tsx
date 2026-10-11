import type { NamesLabels } from '../../../labels';

import { useState } from 'react';

import {
  Box,
  Card,
  Chip,
  Alert,
  Stack,
  Button,
  Switch,
  CardHeader,
  Typography,
  CardContent,
  LinearProgress,
  FormControlLabel,
} from '@mui/material';

import { Iconify } from 'src/shared/ui/iconify';

import { useNameQuiz, useAnswerNameQuiz } from '../../../../application';

/** Card rhythm from full Minimal src/sections/overview/course/course-continue.tsx. */
export function NameQuiz({ labels, introduced }: { labels: NamesLabels; introduced: number }) {
  const create = useNameQuiz();
  const answer = useAnswerNameQuiz();
  const [extra, setExtra] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  const question = create.data?.question;
  const start = () => {
    answer.reset();
    setSelected(null);
    create.mutate(extra);
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
            <Iconify icon="solar:restart-bold" width={24} />
          </Box>
        }
        title={labels.quiz}
        subheader={labels.quizHint}
      />
      <CardContent sx={{ pt: 3, p: { xs: 3, md: 4 } }}>
        <Stack spacing={3}>
          {!question && (
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              alignItems={{ sm: 'center' }}
              justifyContent="space-between"
              spacing={2}
            >
              <FormControlLabel
                control={<Switch checked={extra} onChange={(_, value) => setExtra(value)} />}
                label={labels.practice}
              />
              <Button
                variant="contained"
                loading={create.isPending}
                disabled={introduced < 4}
                onClick={start}
                endIcon={<Iconify icon="eva:arrow-ios-forward-fill" width={16} />}
              >
                {labels.start}
              </Button>
            </Stack>
          )}
          {introduced < 4 && <Alert severity="info">{labels.noQuiz}</Alert>}
          {create.isSuccess && !question && introduced >= 4 && (
            <Alert severity="info">{labels.noQuiz}</Alert>
          )}
          {question && (
            <>
              <Box sx={{ p: 3, borderRadius: 2, bgcolor: 'background.neutral' }}>
                <Stack spacing={1.5}>
                  <Chip
                    label={labels.review}
                    color="primary"
                    size="small"
                    variant="soft"
                    sx={{ alignSelf: 'flex-start' }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {labels[question.quizType]}
                  </Typography>
                  <Typography
                    variant={question.quizType === 'number_name' ? 'h3' : 'h5'}
                    sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}
                  >
                    {question.prompt}
                  </Typography>
                </Stack>
              </Box>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                  gap: 1.5,
                }}
              >
                {question.options.map((option, index) => {
                  const correct = Boolean(answer.data && index === answer.data.correctOption);
                  const wrong = Boolean(
                    answer.data && !answer.data.isCorrect && selected === index
                  );
                  const active = selected === index;
                  return (
                    <Button
                      key={index}
                      variant="outlined"
                      color={correct ? 'success' : wrong ? 'error' : active ? 'primary' : 'inherit'}
                      disabled={answer.isPending || Boolean(answer.data)}
                      onClick={() => {
                        setSelected(index);
                        answer.mutate({ id: question.id, option: index });
                      }}
                      sx={(theme) => ({
                        p: 2,
                        minHeight: 80,
                        textAlign: 'left',
                        justifyContent: 'flex-start',
                        gap: 2,
                        fontSize: 16,
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
                      {option.label}
                    </Button>
                  );
                })}
              </Box>
              {answer.isPending && <LinearProgress />}
              {answer.data && (
                <>
                  <Alert severity={answer.data.isCorrect ? 'success' : 'warning'}>
                    <Typography variant="subtitle2">
                      {answer.data.isCorrect ? labels.correct : labels.incorrect}
                    </Typography>
                    {labels.answer}: {answer.data.answerLabel}
                    {answer.data.answerMeaning && (
                      <Typography variant="body2">{answer.data.answerMeaning}</Typography>
                    )}
                  </Alert>
                  <Button
                    variant="contained"
                    loading={create.isPending}
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
          {(create.error || answer.error) && (
            <Alert severity="error">{(create.error || answer.error)?.message}</Alert>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
