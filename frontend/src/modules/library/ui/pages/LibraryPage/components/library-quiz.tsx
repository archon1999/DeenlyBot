import type { LibraryLabels } from '../../../labels';
import type { LibraryFilter } from '../../../../domain';

import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { PracticeQuiz } from 'src/shared/ui/practice-quiz';

import { useLibraryQuiz, useAnswerLibraryQuiz } from '../../../../application';

export function LibraryQuiz({
  kind,
  labels,
  introduced,
  audioCount = 0,
  itemId,
}: {
  kind: LibraryFilter;
  labels: LibraryLabels;
  introduced: number;
  audioCount?: number;
  itemId?: number;
}) {
  const create = useLibraryQuiz(kind, itemId);
  const answer = useAnswerLibraryQuiz();
  const question = create.data;
  return (
    <PracticeQuiz
      labels={labels}
      introduced={introduced}
      initialExtra={Boolean(itemId)}
      audioCount={audioCount}
      modeLabels={{
        text: labels.textPractice,
        listening: labels.listeningPractice,
        audioLocked: labels.audioLocked,
        audioNoQuiz: labels.audioNoQuiz,
      }}
      icon={<OutlineIcon name="library" width={24} />}
      question={
        question
          ? {
              prompt: question.prompt,
              title: labels[question.quizType],
              options: question.options,
              audioTracks: question.audioTracks,
              arabicPrompt: ['arabic_meaning', 'arabic_title'].includes(question.quizType),
              arabicOptions: ['meaning_arabic', 'title_arabic', 'audio_arabic'].includes(
                question.quizType
              ),
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
