'use client';

import { useQuery, UseQueryOptions } from 'react-query';
import coalitionService, {
  CoalitionStats,
  ContentItem,
  CoalitionMember,
  AdminCoalitionOverview,
  MemberListResponse
} from '@/services/coalitionService';

export function useCoalitionStats(
  options?: Omit<UseQueryOptions<CoalitionStats, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<CoalitionStats, Error>(
    ['coalitionStats'],
    () => coalitionService.getCoalitionStats(),
    {
      staleTime: 60000, // 1 minute
      retry: 2,
      ...options,
    }
  );
}

export function useTopContent(
  limit: number = 10,
  options?: Omit<UseQueryOptions<ContentItem[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<ContentItem[], Error>(
    ['topContent', limit],
    () => coalitionService.getTopContent(limit),
    {
      staleTime: 60000, // 1 minute
      retry: 2,
      ...options,
    }
  );
}

export function useMemberInfo(
  options?: Omit<UseQueryOptions<CoalitionMember, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<CoalitionMember, Error>(
    ['memberInfo'],
    () => coalitionService.getMemberInfo(),
    {
      staleTime: 300000, // 5 minutes
      retry: 2,
      ...options,
    }
  );
}

export function useAdminOverview(
  options?: Omit<UseQueryOptions<AdminCoalitionOverview, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<AdminCoalitionOverview, Error>(
    ['adminCoalitionOverview'],
    () => coalitionService.getAdminOverview(),
    {
      staleTime: 60000, // 1 minute
      retry: 2,
      ...options,
    }
  );
}

export function useCoalitionMembers(
  skip: number = 0,
  limit: number = 50,
  options?: Omit<UseQueryOptions<MemberListResponse, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<MemberListResponse, Error>(
    ['coalitionMembers', skip, limit],
    () => coalitionService.getMembers(skip, limit),
    {
      staleTime: 60000, // 1 minute
      retry: 2,
      ...options,
    }
  );
}
