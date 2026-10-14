import type { ContentProvenance } from 'src/shared/domain/content-provenance';

import { Box, Link, Stack, Typography } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

const copy = {
  uz: {
    title: 'Manba va izoh',
    open: 'Havolani ochish',
    meaning: 'Ma’no bayoni',
    summary: 'Qisqacha mazmun',
    missing: 'Bu materialning manba havolasi hali ko‘rsatilmagan.',
    text: 'Ma’no bayoni o‘rganish uchun berilgan. Havolada asl matn va boshqa tarjimalarni solishtirishingiz mumkin.',
    short: 'Bu qisqartirilgan mazmun, to‘liq tarjima emas.',
    name: 'An’anaviy ismlar ro‘yxati. Havola rivoyatga tegishli; har bir ismning ma’nosi va izohining alohida manbasi sifatida berilmagan.',
    lesson: 'Bu til o‘rganish materiali. Namoz iboralari ma’nosi bilan fiqhiy hukmlarni farqlang.',
    analysis: 'Bu lug‘aviy va grammatik izoh. To‘liq tafsir o‘rnini bosmaydi.',
  },
  ru: {
    title: 'Источник и пояснение',
    open: 'Открыть ссылку',
    meaning: 'Изложение смысла',
    summary: 'Краткий смысл',
    missing: 'Ссылка на источник этого материала пока не указана.',
    text: 'Смысл изложен для обучения. По ссылке можно сопоставить исходный текст и другие переводы.',
    short: 'Это сокращённое изложение, а не полный перевод.',
    name: 'Традиционный перечень имён. Ссылка ведёт к преданию и не является отдельным источником каждого значения или пояснения.',
    lesson:
      'Материал для изучения языка. Значение молитвенных выражений следует отличать от правовых предписаний.',
    analysis: 'Лексическое и грамматическое пояснение, не замена полному тафсиру.',
  },
  en: {
    title: 'Source and context',
    open: 'Open reference',
    meaning: 'Meaning for study',
    summary: 'Concise meaning',
    missing: 'A source reference has not yet been provided for this material.',
    text: 'The meaning is presented for study. The reference lets you compare the original text and other translations.',
    short: 'This is an abridged meaning, not a full translation.',
    name: 'A traditional enumeration of names. The link refers to a narration, not a separate source for every meaning or explanation.',
    lesson:
      'Language learning material. Meanings of prayer expressions are distinct from rulings on prayer.',
    analysis: 'Lexical and grammatical notes, not a replacement for a full tafsir.',
  },
};

export function useMeaningLabel(source?: ContentProvenance) {
  const labels = copy[useLocale().language];
  return source?.meaningIsSummary ? labels.summary : labels.meaning;
}

export function ContentSource({ source }: { source?: ContentProvenance }) {
  const labels = copy[useLocale().language];
  const note =
    source?.kind === 'name'
      ? labels.name
      : source?.kind === 'lesson'
        ? labels.lesson
        : source?.kind === 'analysis'
          ? labels.analysis
          : labels.text;
  return (
    <Box sx={{ p: 2.5, borderRadius: 2, bgcolor: 'background.neutral' }}>
      <Stack spacing={1}>
        <Typography variant="subtitle2">{labels.title}</Typography>
        {source ? (
          <>
            <Typography variant="body2" sx={{ overflowWrap: 'anywhere' }}>
              {source.reference || source.title}
            </Typography>
            {source.meaningIsSummary && <Typography variant="body2">{labels.short}</Typography>}
            <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.8 }}>
              {note}
            </Typography>
            {source.url && (
              <Link
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  display: 'inline-flex',
                  gap: 1,
                  alignItems: 'center',
                  alignSelf: 'flex-start',
                  minHeight: 44,
                  typography: 'body2',
                }}
              >
                {labels.open}
                <OutlineIcon name="link" width={18} />
              </Link>
            )}
          </>
        ) : (
          <Typography variant="body2" color="text.secondary">
            {labels.missing}
          </Typography>
        )}
      </Stack>
    </Box>
  );
}
