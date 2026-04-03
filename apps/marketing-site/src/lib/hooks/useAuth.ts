import { useState } from 'react';
import { useToast } from '@encypher/design-system';
import { signIn as nextAuthSignIn } from 'next-auth/react';
import { fetchApi } from "../api";

/**
 * useAuth - Custom hook for managing authentication state and API calls.
 *
 * Usage:
 *   const { signIn, signUp, user, loading, error } = useAuth();
 *
 * - signIn(email, password): Promise<void>
 * - signUp(email, password, confirm): Promise<void>
 * - user: Authenticated user object or null
 * - loading: boolean
 * - error: string | null
 *
 * Handles API calls to NEXT_PUBLIC_API_BASE_URL, manages loading/error state,
 * and provides a simple interface for auth flows. Intended for use in modular
 * auth forms and onboarding flows.
 */
interface AuthResponse {
  success: boolean;
  error?: { message: string };
  data?: { uuid: string; email: string; role: string };
}

export function useAuth() {
  const [user, setUser] = useState<{ uuid: string; email: string; role: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  async function signIn(email: string, password: string) {
    setLoading(true); setError(null);
    try {
      // Use NextAuth credentials provider
      const result = await nextAuthSignIn("credentials", {
        email,
        password,
        redirect: false,
      });
      if (!result?.ok) throw new Error(result?.error || 'Sign in failed');
      // Optionally fetch user info from session here
      setUser(null); // Reset user; real user info should be loaded from session
      toast({ title: 'Signed in successfully!', variant: 'success' });
    } catch (e) {
      const err = e as Error;
      setError(err.message);
      toast({ title: err.message, variant: 'error' });
    } finally {
      setLoading(false);
    }
  }

  async function signUp(email: string, password: string, confirm: string, orgName?: string) {
    setLoading(true); setError(null);
    if (password !== confirm) {
      setError('Passwords do not match');
      toast({ title: 'Passwords do not match', variant: 'error' });
      setLoading(false); return;
    }
    try {
      const res = await fetchApi("/auth/register", {
        method: "POST",
        body: JSON.stringify(orgName ? { email, password, org_name: orgName } : { email, password }),
      }) as AuthResponse;
      if (!res.success) throw new Error(res.error?.message || 'Sign up failed');
      // Do not set user or redirect here; registration requires email verification
      toast({ title: 'Account created! Please verify your email to activate your account.', variant: 'success' });
    } catch (e) {
      const err = e as Error;
      setError(err.message);
      toast({ title: err.message, variant: 'error' });
    } finally {
      setLoading(false);
    }
  }

  return { signIn, signUp, user, loading, error };
}
