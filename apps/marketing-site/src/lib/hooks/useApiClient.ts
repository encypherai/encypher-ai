import { useSession } from 'next-auth/react';
import { fetchApi } from '../api';
import { useCallback } from 'react';

// Define custom session type with the backend token
interface CustomSession {
  accessToken?: string;
  user?: {
    id?: string;
    name?: string | null;
    email?: string | null;
    image?: string | null;
    user_uuid?: string;
    role?: string;
  };
  error?: string;
}

/**
 * Custom hook that provides an authenticated API client using the backend token
 * from the NextAuth session.
 * 
 * This ensures that API calls to the backend use the correct token (the backend-issued JWT)
 * rather than the OAuth provider token.
 */
interface ApiClientOptions extends RequestInit {
  isPublic?: boolean;
}

export function useApiClient() {
  const { data: session } = useSession();

  const apiCall = useCallback(async <T>(
    path: string,
    options: ApiClientOptions = {}
  ): Promise<T> => {
    const { isPublic, ...fetchOptions } = options;
    const backendToken = (session as unknown as CustomSession)?.accessToken;

    if (!backendToken && !isPublic) {
      console.error('No backend token available for a protected API call to', path);
      throw new Error('No backend token available');
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const url = `${baseUrl}${path}`;

    return fetchApi<T>(url, {
      ...fetchOptions,
      token: backendToken, // fetchApi will handle the token being undefined
      headers: {
        ...fetchOptions.headers,
      },
    });
  }, [session]);

  return {
    apiCall,
    isAuthenticated: !!(session as unknown as CustomSession)?.accessToken,
    session: session as unknown as CustomSession,
  };
}
