'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { AuthProvider } from '@/lib/auth';
import { NotificationProvider } from '@/lib/notifications';
import { ThemeProvider } from '@/lib/theme';

export default function ClientProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  // Create a client for React Query with enhanced caching strategy
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Stale-while-revalidate pattern
        staleTime: 5 * 60 * 1000, // Data is fresh for 5 minutes
        cacheTime: 10 * 60 * 1000, // Cache data for 10 minutes
        refetchOnWindowFocus: 'always', // Refetch when window regains focus
        refetchOnMount: true, // Refetch when component mounts
        refetchOnReconnect: true, // Refetch when network reconnects
        retry: 2, // Retry failed requests twice
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
        // Show stale data while fetching new data
        keepPreviousData: true,
      },
      mutations: {
        retry: 1, // Retry failed mutations once
        retryDelay: 1000, // Wait 1 second before retrying
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <NotificationProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </NotificationProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
