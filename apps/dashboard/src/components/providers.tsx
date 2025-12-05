'use client';

import { ReactNode, useState } from 'react';
import { SessionProvider, signOut } from 'next-auth/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster, toast } from 'sonner';
import { OrganizationProvider } from '../contexts/OrganizationContext';
import { NotificationProvider } from '../contexts/NotificationContext';
import { ThemeProvider } from '../contexts/ThemeContext';
import { CommandPalette } from './CommandPalette';

interface ProvidersProps {
  children: ReactNode;
}

// Helper to check if error is an auth error
function isAuthError(error: unknown): boolean {
  if (error instanceof Error && 'statusCode' in error) {
    const statusCode = (error as { statusCode: number }).statusCode;
    return statusCode === 401 || statusCode === 403;
  }
  return false;
}

// Track if we're already handling logout to prevent multiple redirects
let isLoggingOut = false;

async function handleAuthError() {
  if (isLoggingOut) return;
  isLoggingOut = true;
  
  toast.error('Your session has expired. Please sign in again.');
  
  // Use window.location for guaranteed redirect
  await signOut({ redirect: false });
  window.location.href = '/login';
}

export function Providers({ children }: ProvidersProps) {
  // Create QueryClient with global error handling for auth errors
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Retry once on failure, but not on auth errors
        retry: (failureCount, error) => {
          if (isAuthError(error)) {
            // Trigger logout on auth error
            handleAuthError();
            return false;
          }
          return failureCount < 1;
        },
        // Stale time of 30 seconds to reduce unnecessary refetches
        staleTime: 30 * 1000,
      },
      mutations: {
        // Handle auth errors globally for mutations
        onError: async (error) => {
          if (isAuthError(error)) {
            await handleAuthError();
          }
        },
      },
    },
  }));

  return (
    <SessionProvider
      // Refetch session every 5 minutes to detect expired backend tokens
      refetchInterval={5 * 60}
      // Refetch when window regains focus (user returns to tab)
      refetchOnWindowFocus={true}
    >
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <NotificationProvider>
            <OrganizationProvider>
              {children}
              <CommandPalette />
              <Toaster richColors position="top-right" />
            </OrganizationProvider>
          </NotificationProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </SessionProvider>
  );
}

export default Providers;
