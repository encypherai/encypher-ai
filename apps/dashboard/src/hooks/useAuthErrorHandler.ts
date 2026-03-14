'use client';

import { useCallback } from 'react';
import { signOut } from 'next-auth/react';
import { toast } from 'sonner';
import { isSessionExpiredError } from '../lib/session-errors';

/**
 * Hook to handle authentication errors from API calls.
 * Automatically signs out the user when their session has expired.
 * Does NOT sign out for tier-gated 401/403 errors.
 */
export function useAuthErrorHandler() {
  const handleAuthError = useCallback(async (error: unknown) => {
    if (isSessionExpiredError(error)) {
      toast.error('Your session has expired. Please sign in again.');

      // Sign out and redirect to login
      await signOut({
        callbackUrl: '/login?reason=session_expired',
        redirect: true,
      });
      return true; // Indicates auth error was handled
    }

    return false; // Not a session expiry error
  }, []);

  return { handleAuthError };
}
