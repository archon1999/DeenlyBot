import { useQuery } from '@tanstack/react-query';

import { settingsKeys } from './keys';
import { settingsRepository } from '../data-access';

export const useUserSettings = () =>
  useQuery({ queryKey: settingsKeys.all, queryFn: settingsRepository.get });
