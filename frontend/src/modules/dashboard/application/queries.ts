import { useQuery } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { dashboardKeys } from './keys';
import { dashboardRepository } from '../data-access';

export const useDashboard = () => {
  const { language } = useLocale();
  return useQuery({
    queryKey: dashboardKeys.list(language),
    queryFn: dashboardRepository.overview,
  });
};
