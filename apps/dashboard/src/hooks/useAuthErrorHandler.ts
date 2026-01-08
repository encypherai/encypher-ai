'use client';

import { useCallback } from 'react';
import { signOut } from 'next-auth/react';
import { toast } from 'sonner';

/**
 * Check if an error indicates a true session expiry vs a permission/tier error.
 * 
 * - 401 with "expired", "invalid token", or "not authenticated" = session expired
 * - 401 from tier-gated endpoints (templates, team, audit) = NOT session expired
 * - 403 = permission denied, NOT session expired
 */
function isSessionExpiredError(error: unknown): boolean {
  // Get status code
  let statusCode: number | undefined;
  let errorMessage = '';
  
  if (error instanceof Error && 'statusCode' in error) {
    statusCode = (error as { statusCode: number }).statusCode;
    errorMessage = error.message.toLowerCase();
  } else if (error instanceof Response) {
    statusCode = error.status;
  }
  
  // 403 is always "forbidden" (permission denied), not session expiry
  if (statusCode === 403) {
    return false;
  }
  
  // 401 could be session expiry OR tier-gated endpoint returning unauthorized
  if (statusCode === 401) {
    // Check for tier-related error messages (not session expiry)
    const tierRelatedMessages = [
      'tier', 'upgrade', 'plan', 'subscription', 'business', 'enterprise',
      'professional', 'feature', 'access denied', 'permission'
    ];
    
    if (tierRelatedMessages.some(msg => errorMessage.includes(msg))) {
      return false; // Tier-gated, not session expiry
    }
    
    // Check for true session expiry messages
    const sessionExpiredMessages = [
      'expired', 'invalid token', 'not authenticated', 'session', 
      'jwt', 'token invalid', 'unauthorized'
    ];
    
    // Only treat as session expiry if message indicates it
    // OR if there's no specific message (generic 401)
    if (sessionExpiredMessages.some(msg => errorMessage.includes(msg)) || !errorMessage) {
      return true;
    }
  }
  
  return false;
}

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
        callbackUrl: '/login',
        redirect: true,
      });
      return true; // Indicates auth error was handled
    }

    return false; // Not a session expiry error
  }, []);

  return { handleAuthError };
}

/**
 * Wrapper function to handle API errors with automatic auth error handling.
 * Use this in React Query's onError callbacks.
 */
export function createAuthErrorHandler(signOutFn: typeof signOut) {
  return async (error: unknown): Promise<boolean> => {
    if (isSessionExpiredError(error)) {
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
