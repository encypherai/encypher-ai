'use client';

import { useSession } from 'next-auth/react';
import {
  useQuery,
  useMutation,
  type UndefinedInitialDataOptions,
  type UseMutationOptions,
} from '@tanstack/react-query';

/**
 * Extract the access token from the NextAuth session.
 */
export function useAccessToken(): string | undefined {
  const { data: session } = useSession();
  return (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
}

/**
 * Wrapper around useQuery that automatically injects the session access token
 * and disables the query until the token is available.
 *
 * Uses @tanstack/react-query v5 types.
 */
export function useAuthenticatedQuery<T>(
  queryKey: unknown[],
  queryFn: (accessToken: string) => Promise<T>,
  options?: Omit<
    UndefinedInitialDataOptions<T, Error, T, unknown[]>,
    'queryKey' | 'queryFn' | 'enabled'
  >
) {
  const accessToken = useAccessToken();
  return useQuery<T, Error, T, unknown[]>({
    queryKey,
    queryFn: () => queryFn(accessToken!),
    enabled: Boolean(accessToken),
    ...options,
  });
}

/**
 * Wrapper around useMutation that automatically injects the session access token.
 */
export function useAuthenticatedMutation<TData, TVariables>(
  mutationFn: (accessToken: string, variables: TVariables) => Promise<TData>,
  options?: Omit<UseMutationOptions<TData, Error, TVariables>, 'mutationFn'>
) {
  const accessToken = useAccessToken();
  return useMutation<TData, Error, TVariables>({
    mutationFn: (variables: TVariables) => mutationFn(accessToken!, variables),
    ...options,
  });
}
