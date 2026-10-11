import { useQuery } from '@tanstack/react-query';

import { useLocale } from 'src/shared/i18n';

import { calendarKeys } from './keys';
import { calendarRepository } from '../data-access';

export const useCalendar = () => {
  const { language } = useLocale();
  return useQuery({ queryKey: calendarKeys.list(language), queryFn: calendarRepository.events });
};
