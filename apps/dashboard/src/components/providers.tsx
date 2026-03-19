'use client';

import { ReactNode, Suspense, useState } from 'react';
import { SessionProvider, signOut } from 'next-auth/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster, toast } from 'sonner';
import { OrganizationProvider } from '../contexts/OrganizationContext';
import { NotificationProvider } from '../contexts/NotificationContext';
import { ThemeProvider } from '../contexts/ThemeContext';
import { DemoModeProvider } from '../contexts/DemoModeContext';
import { CommandPalette } from './CommandPalette';
import { ApiError } from '../lib/api';
import { isSessionExpiredError } from '../lib/session-errors';

interface ProvidersProps {
  children: ReactNode;
}

// Track if we're already handling logout to prevent multiple redirects
let isLoggingOut = false;

async function handleAuthError() {
  if (isLoggingOut) return;
  isLoggingOut = true;

  toast.error('Your session has expired. Please sign in again.');

  // Use window.location for guaranteed redirect
  await signOut({ redirect: false });
  window.location.href = '/login?reason=session_expired';
}

export function Providers({ children }: ProvidersProps) {
  // Create QueryClient with global error handling for auth errors
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Retry once on failure, but not on session expiry errors
        retry: (failureCount, error) => {
          if (isSessionExpiredError(error)) {
            // Trigger logout on session expiry
            handleAuthError();
            return false;
          }
          return failureCount < 1;
        },
        // Stale time of 30 seconds to reduce unnecessary refetches
        staleTime: 30 * 1000,
      },
      mutations: {
        onError: async (error) => {
          if (isSessionExpiredError(error)) {
            await handleAuthError();
            return;
          }
          // Rate limit: show specific guidance
          if (error instanceof ApiError && error.statusCode === 429) {
            toast.error('Rate limit reached', {
              description: error.nextAction || 'Please wait a moment before retrying.',
            });
            return;
          }
          // For all other errors: show next_action as toast description when available
          if (error instanceof ApiError && error.nextAction) {
            toast.error(error.message, { description: error.nextAction });
          }
        },
      },
    },
  }));

  return (
    <SessionProvider
      // Poll session every 4 minutes - triggers JWT callback which handles silent token refresh.
      // Backend access tokens last 8h; this ensures refresh happens well before expiry.
      refetchInterval={4 * 60}
      // Re-validate immediately when the user returns to the tab
      refetchOnWindowFocus={true}
    >
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <NotificationProvider>
            <OrganizationProvider>
              <Suspense fallback={null}>
                <DemoModeProvider>
                  {children}
                </DemoModeProvider>
              </Suspense>
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
