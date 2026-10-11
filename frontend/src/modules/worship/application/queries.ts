import { useQuery } from '@tanstack/react-query';

import { worshipKeys } from './keys';
import { worshipRepository } from '../data-access';

export const useQada = () =>
  useQuery({ queryKey: worshipKeys.all, queryFn: worshipRepository.summary });
