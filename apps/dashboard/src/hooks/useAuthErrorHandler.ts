'use client';

import { useCallback } from 'react';
import { signOut } from 'next-auth/react';
import { toast } from 'sonner';

/**
 * Hook to handle authentication errors from API calls.
 * Automatically signs out the user when their session has expired.
 */
export function useAuthErrorHandler() {
  const handleAuthError = useCallback(async (error: unknown) => {
    // Check if this is an auth error (401/403)
    const isAuthError = 
      (error instanceof Error && 'statusCode' in error && 
       ((error as { statusCode: number }).statusCode === 401 || 
        (error as { statusCode: number }).statusCode === 403)) ||
      (error instanceof Response && (error.status === 401 || error.status === 403));

    if (isAuthError) {
      toast.error('Your session has expired. Please sign in again.');
      
      // Sign out and redirect to login
      await signOut({ 
        callbackUrl: '/login',
        redirect: true,
      });
      return true; // Indicates auth error was handled
    }

    return false; // Not an auth error
  }, []);

  return { handleAuthError };
}

/**
 * Wrapper function to handle API errors with automatic auth error handling.
 * Use this in React Query's onError callbacks.
 */
export function createAuthErrorHandler(signOutFn: typeof signOut) {
  return async (error: unknown): Promise<boolean> => {
    const isAuthError = 
      (error instanceof Error && 'statusCode' in error && 
       ((error as { statusCode: number }).statusCode === 401 || 
        (error as { statusCode: number }).statusCode === 403));

    if (isAuthError) {
      toast.error('Your session has expired. Please sign in again.');
      await signOutFn({ 
        callbackUrl: '/login',
        redirect: true,
      });
      return true;
    }

    return false;
  };
}
