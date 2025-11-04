'use client';

import { useQuery, UseQueryOptions } from 'react-query';
import auditLogService, { AuditLogFilters, AuditLogResponse } from '@/services/auditLogService';

export function useAuditLogs(
  filters: AuditLogFilters = {},
  options?: Omit<UseQueryOptions<AuditLogResponse, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<AuditLogResponse, Error>(
    ['auditLogs', filters],
    () => auditLogService.getAuditLogs(filters),
    {
      staleTime: 30000, // 30 seconds
      retry: 2,
      ...options,
    }
  );
}

export function useAuditLogStats(
  options?: Omit<UseQueryOptions<any, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery(
    ['auditLogStats'],
    () => auditLogService.getAuditLogStats(),
    {
      staleTime: 60000, // 1 minute
      retry: 2,
      ...options,
    }
  );
}
