import { useQuery } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { namesKeys } from './keys';
import { namesRepository } from '../data-access';

export const useNames = () => {
  const { language } = useLocale();
  return useQuery({ queryKey: namesKeys.list(language), queryFn: namesRepository.overview });
};
