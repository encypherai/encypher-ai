'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

/**
 * Hook to require authentication on a page.
 * Redirects to login if user is not authenticated.
 * 
 * @param redirectTo - Optional path to redirect to after login (default: current page)
 * @returns Session data and loading state
 */
export function useRequireAuth(redirectTo?: string) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return; // Still checking session

    if (status === 'unauthenticated') {
      // User is not authenticated, redirect to login
      const currentPath = redirectTo || window.location.pathname;
      const loginUrl = `/login?callbackUrl=${encodeURIComponent(currentPath)}`;
      router.push(loginUrl);
    }
  }, [status, router, redirectTo]);

  return {
    session,
    status,
    isLoading: status === 'loading',
    isAuthenticated: status === 'authenticated',
    accessToken: (session?.user as any)?.accessToken as string | undefined,
  };
}
