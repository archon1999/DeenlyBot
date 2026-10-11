import { useQuery } from '@tanstack/react-query';

import { reportsKeys } from './keys';
import { reportsRepository } from '../data-access';

export const useReports = () =>
  useQuery({ queryKey: reportsKeys.all, queryFn: reportsRepository.overview });
