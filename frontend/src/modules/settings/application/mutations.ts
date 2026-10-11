import type { UserSettings } from '../domain';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { settingsKeys } from './keys';
import { settingsRepository } from '../data-access';

export const useSaveSettings = () => {
  const client = useQueryClient();
  const { setLanguage } = useLocale();
  return useMutation({
    mutationFn: (params: UserSettings) => settingsRepository.save(params),
    onSuccess: async (data) => {
      client.setQueryData(settingsKeys.all, data);
      setLanguage(data.language);
      await client.invalidateQueries();
    },
  });
};
