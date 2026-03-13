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

/**
 * Check if an error indicates a true session expiry vs a permission/tier error.
 *
 * - 401 with session-related messages = session expired
 * - 401 from tier-gated endpoints = NOT session expired (don't logout)
 * - 403 = permission denied, NOT session expired
 */
function isSessionExpiredError(error: unknown): boolean {
  let statusCode: number | undefined;
  let errorMessage = '';

  if (error instanceof Error && 'statusCode' in error) {
    statusCode = (error as { statusCode: number }).statusCode;
    errorMessage = error.message.toLowerCase();
  }

  // 403 is always "forbidden" (permission denied), not session expiry
  if (statusCode === 403) {
    return false;
  }

  // 401 could be session expiry OR tier-gated endpoint
  if (statusCode === 401) {
    // Check for tier-related error messages (not session expiry)
    const tierRelatedMessages = [
      'tier', 'upgrade', 'plan', 'subscription', 'business', 'enterprise',
      'professional', 'feature', 'access denied', 'permission', 'template'
    ];

    if (tierRelatedMessages.some(msg => errorMessage.includes(msg))) {
      return false; // Tier-gated, not session expiry
    }

    // Check for true session expiry messages
    const sessionExpiredMessages = [
      'expired', 'invalid token', 'not authenticated', 'session invalid',
      'jwt', 'token invalid'
    ];

    // Only treat as session expiry if message explicitly indicates it
    if (sessionExpiredMessages.some(msg => errorMessage.includes(msg))) {
      return true;
    }

    // Generic 401 with no message body - backend always includes a description
    // for tier/permission issues, so a bare 401 most likely means token expiry.
    if (!errorMessage) {
      return true;
    }
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
        // Handle session expiry errors globally for mutations
        onError: async (error) => {
          if (isSessionExpiredError(error)) {
            await handleAuthError();
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
