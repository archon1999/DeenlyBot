import { Box, Alert, Stack, Button, Skeleton } from '@mui/material';

import { useLocale } from 'src/shared/i18n';

type QueryStateProps = {
  isPending: boolean;
  error?: unknown;
  onRetry?: () => unknown;
  children: React.ReactNode;
};
export function QueryState({ isPending, error, onRetry, children }: QueryStateProps) {
  const { language } = useLocale();
  const labels = {
    uz: { error: 'Ma’lumotlarni yuklab bo‘lmadi', retry: 'Qayta urinish' },
    ru: { error: 'Не удалось загрузить данные', retry: 'Повторить' },
    en: { error: 'Unable to load data', retry: 'Try again' },
  }[language];
  if (isPending)
    return (
      <Stack spacing={2} aria-busy="true">
        <Skeleton height={80} />
        <Skeleton variant="rounded" height={220} />
      </Stack>
    );
  if (error)
    return (
      <Alert
        severity="error"
        action={
          onRetry && (
            <Button color="inherit" onClick={onRetry}>
              {labels.retry}
            </Button>
          )
        }
      >
        <Box>{labels.error}</Box>
        {error instanceof Error && error.message}
      </Alert>
    );
  return <>{children}</>;
}
