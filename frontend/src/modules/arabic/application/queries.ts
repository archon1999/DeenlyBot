import { useQuery } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { arabicKeys } from './keys';
import { arabicRepository } from '../data-access';

export const useArabic = () => {
  const { language } = useLocale();
  return useQuery({ queryKey: arabicKeys.list(language), queryFn: arabicRepository.overview });
};
export const useArabicLesson = (id: number | null) => {
  const { language } = useLocale();
  return useQuery({
    queryKey: arabicKeys.detail(language, id),
    queryFn: () => arabicRepository.lesson(id!),
    enabled: id !== null,
  });
};
