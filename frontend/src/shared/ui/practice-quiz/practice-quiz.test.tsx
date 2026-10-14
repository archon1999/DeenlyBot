import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import { PracticeQuiz } from './index';

const labels = {
  quiz: 'Review',
  quizHint: 'Review studied materials',
  practice: 'Extra practice',
  review: 'Start',
  again: 'Again',
  quizLocked: 'Study four materials',
  noQuiz: 'No question',
  correct: 'Correct',
  incorrect: 'Try again',
  answer: 'Answer',
};
const base = {
  labels,
  introduced: 4,
  creating: false,
  answering: false,
  noQuestion: false,
  onStart: () => {},
  onAnswer: () => {},
  icon: <span>Book</span>,
};
const render = (props: Parameters<typeof PracticeQuiz>[0]) =>
  renderToStaticMarkup(
    <ThemeProvider theme={createTheme({ cssVariables: true })}>
      <PracticeQuiz {...props} />
    </ThemeProvider>
  );

it('shows a locked review without creating fake progress', () => {
  const html = render({ ...base, introduced: 0 });
  expect(html).toContain(labels.quizLocked);
  expect(html).toMatch(/<button[^>]*disabled=""/);
  expect(html).toContain(labels.practice);
});
it('renders four Arabic options in RTL with readable long text', () => {
  const html = render({
    ...base,
    question: {
      title: 'Choose Arabic text',
      prompt: 'Meaning',
      arabicPrompt: false,
      arabicOptions: true,
      options: ['أ', 'ب', 'ت', 'ث'].map((label) => ({ label })),
    },
  });
  expect(html.match(/lang="ar" dir="rtl"/g)).toHaveLength(4);
  expect(html).toContain('overflow-wrap:anywhere');
  expect(html).toContain('Amiri');
  expect(html).not.toContain(labels.correct);
});
it('shows stored feedback, prevents a second answer and offers another question', () => {
  const html = render({
    ...base,
    question: {
      title: 'Choose meaning',
      prompt: 'أ',
      arabicPrompt: true,
      arabicOptions: false,
      options: ['One', 'Two', 'Three', 'Four'].map((label) => ({ label })),
    },
    result: { isCorrect: true, correctOption: 1, answerLabel: 'Two', answerMeaning: 'Meaning' },
  });
  expect(html).toContain('lang="ar" dir="rtl"');
  expect(html).toContain(labels.correct);
  expect(html).toContain('Meaning');
  expect(html).toContain(labels.again);
  expect(html.match(/<button[^>]*disabled=""/g)).toHaveLength(4);
});
it('offers listening mode without inventing studied audio eligibility', () => {
  const html = render({
    ...base,
    audioCount: 0,
    modeLabels: {
      text: 'Text practice',
      listening: 'Listening practice',
      audioLocked: 'Study four audio items',
      audioNoQuiz: 'No audio question',
    },
  });
  expect(html).toContain('Text practice');
  expect(html).toContain('Listening practice');
  expect(html).not.toContain('src=');
  expect(html).toContain('padding:6px');
});
