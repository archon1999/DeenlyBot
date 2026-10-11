import type { ArabicLabels } from '../../../labels';

import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { PracticeQuiz } from 'src/shared/ui/practice-quiz';

import { useArabicQuiz, useAnswerArabicQuiz } from '../../../../application';

export function ArabicQuiz({
  labels,
  introduced,
  audioCount = 0,
}: {
  labels: ArabicLabels;
  introduced: number;
  audioCount?: number;
}) {
  const create = useArabicQuiz();
  const answer = useAnswerArabicQuiz();
  const question = create.data;
  return (
    <PracticeQuiz
      labels={labels}
      introduced={introduced}
      audioCount={audioCount}
      modeLabels={{
        text: labels.textPractice,
        listening: labels.listeningPractice,
        audioLocked: labels.audioLocked,
        audioNoQuiz: labels.audioNoQuiz,
      }}
      icon={<OutlineIcon name="arabic" width={24} />}
      question={
        question
          ? {
              prompt: question.prompt,
              title: labels[question.quizType],
              options: question.options,
              audioTracks: question.audioTracks,
              arabicPrompt: ['arabic_meaning', 'arabic_transcription', 'missing_word'].includes(
                question.quizType
              ),
              arabicOptions: [
                'meaning_arabic',
                'transcription_arabic',
                'missing_word',
                'audio_arabic',
              ].includes(question.quizType),
            }
          : null
      }
      result={answer.data}
      creating={create.isPending}
      answering={answer.isPending}
      noQuestion={create.isSuccess && !question}
      error={create.error || answer.error}
      onStart={(extra, mode) => {
        answer.reset();
        create.reset();
        create.mutate({ extra, mode });
      }}
      onAnswer={(option) => {
        if (question) answer.mutate({ id: question.id, option });
      }}
    />
  );
}
