'use client';

import { Input } from '@encypher/design-system';
import { useState } from 'react';
import { signIn } from 'next-auth/react';
import Image from 'next/image';
import apiClient from '../../lib/api';

// Note: API_BASE not used directly in login - auth goes through NextAuth
import Link from 'next/link';
import MetadataBackground from '../../components/hero/MetadataBackground';

// Canonical SVG logos
const LOGO_COLOR = '/assets/encypher_full_logo_color.svg';
const LOGO_WHITE = '/assets/encypher_full_logo_white.svg';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passkeyLoading, setPasskeyLoading] = useState(false);

  const base64UrlToBuffer = (value: string): Uint8Array => {
    const padded = `${value}${'='.repeat((4 - (value.length % 4)) % 4)}`;
    const base64 = padded.replace(/-/g, '+').replace(/_/g, '/');
    const binary = atob(base64);
    return Uint8Array.from(binary, (char) => char.charCodeAt(0));
  };

  const bufferToBase64Url = (buffer: ArrayBuffer): string => {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    bytes.forEach((b) => {
      binary += String.fromCharCode(b);
    });
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
  };

  const buildPasskeyAssertionPayload = (credential: PublicKeyCredential): Record<string, unknown> => {
    const response = credential.response as AuthenticatorAssertionResponse;
    return {
      id: credential.id,
      rawId: bufferToBase64Url(credential.rawId),
      type: credential.type,
      response: {
        authenticatorData: bufferToBase64Url(response.authenticatorData),
        clientDataJSON: bufferToBase64Url(response.clientDataJSON),
        signature: bufferToBase64Url(response.signature),
        userHandle: response.userHandle ? bufferToBase64Url(response.userHandle) : null,
      },
    };
  };

  const handlePasskeyLogin = async () => {
    if (!email) {
      setError('Enter your email to continue with passkey sign in.');
      return;
    }

    if (typeof window === 'undefined' || !window.PublicKeyCredential) {
      setError('Passkeys are not supported in this browser.');
      return;
    }

    setError('');
    setPasskeyLoading(true);
    try {
      const optionsData = await apiClient.startPasskeyAuthentication(email);
      const options = JSON.parse(optionsData.options_json);
      const publicKey: PublicKeyCredentialRequestOptions = {
        ...options,
        challenge: base64UrlToBuffer(options.challenge),
        allowCredentials: (options.allowCredentials || []).map((cred: any) => ({
          ...cred,
          id: base64UrlToBuffer(cred.id),
        })),
      };

      const credential = (await navigator.credentials.get({ publicKey })) as PublicKeyCredential | null;
      if (!credential) {
        throw new Error('Passkey sign-in was cancelled.');
      }

      const authData = await apiClient.completePasskeyAuthentication(email, buildPasskeyAssertionPayload(credential));
      const accessToken = (authData as any)?.access_token as string | undefined;
      if (!accessToken) {
        throw new Error('Passkey authentication did not return a session token.');
      }

      const result = await signIn('credentials', {
        email,
        password: `__TOKEN__${accessToken}`,
        redirect: false,
        callbackUrl: '/',
      });

      if (result?.error) {
        throw new Error(result.error);
      }
      window.location.href = '/';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Passkey login failed.');
    } finally {
      setPasskeyLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await signIn('credentials', {
        email,
        password,
        mfaToken: mfaToken || undefined,
        mfaCode: mfaCode || undefined,
        redirect: false,
        callbackUrl: '/',
      });

      if (result?.error) {
        if (result.error.startsWith('MFA_REQUIRED:')) {
          setMfaToken(result.error.replace('MFA_REQUIRED:', ''));
          setError('Enter your authentication code to finish signing in.');
          setLoading(false);
          return;
        }
        // NextAuth passes the error message from authorize() in result.error
        setError(result.error === 'CredentialsSignin' ? 'Invalid email or password' : result.error);
        setLoading(false);
      } else if (result?.ok) {
        // Force a hard navigation to ensure middleware re-evaluates with fresh session
        // Using window.location instead of router.push to avoid Next.js cache issues
        window.location.href = '/';
      } else {
        setError('Login failed. Please try again.');
        setLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred. Please try again.');
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen bg-background">
      <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue opacity-60" />
        <div className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl border border-border p-8 relative z-10 transition-all duration-300">
          <div className="flex flex-col gap-6">
            {/* Logo */}
            <div className="flex justify-center mb-2">
              <Link href="/">
                <span className="sr-only">Encypher</span>
                {/* Color logo for light mode */}
                <Image
                  src={LOGO_COLOR}
                  alt="Encypher"
                  width={180}
                  height={45}
                  className="h-10 w-auto object-contain dark:hidden"
                  priority
                />
                {/* White logo for dark mode */}
                <Image
                  src={LOGO_WHITE}
                  alt="Encypher"
                  width={180}
                  height={45}
                  className="h-10 w-auto object-contain hidden dark:block"
                  priority
                />
              </Link>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-card-foreground mb-1">Sign into your account</h1>
              <p className="text-sm text-muted-foreground mb-6">Cryptographic Proof for the AI Economy</p>
            </div>

            <div className="grid grid-cols-2 gap-3 w-full mb-2">
              <button
                type="button"
                disabled={loading}
                onClick={() => signIn('google', { callbackUrl: '/' })}
                className="flex items-center justify-center gap-2 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
                aria-label="Sign in with Google"
                style={{ boxShadow: '0 2px 10px 0 #4285F4' }}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
                <span className="text-base">Google</span>
              </button>
              <button
                type="button"
                disabled={loading}
                onClick={() => signIn('github', { callbackUrl: '/' })}
                className="flex items-center justify-center gap-2 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
                aria-label="Sign in with GitHub"
                style={{ boxShadow: '0 2px 10px 0 #4285F4' }}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.83-.729.83-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                <span className="text-base">GitHub</span>
              </button>
            </div>

            <button
              type="button"
              disabled={loading || passkeyLoading}
              onClick={handlePasskeyLogin}
              className="w-full py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {passkeyLoading ? 'Waiting for passkey…' : 'Sign in with passkey'}
            </button>

            <div className="flex items-center gap-2 my-2">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">or sign in with</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
                  <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">Email</label>
                <Input id="email" type="email" placeholder="Your email address" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={loading} />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">Password</label>
                <Input id="password" type="password" placeholder="Your password" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={loading} />
              </div>

              {mfaToken && (
                <div>
                  <label htmlFor="mfa-code" className="block text-sm font-medium text-foreground mb-2">Authentication code</label>
                  <Input
                    id="mfa-code"
                    type="text"
                    placeholder="6-digit code or backup code"
                    value={mfaCode}
                    onChange={(e) => setMfaCode(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-primary text-primary-foreground hover:bg-primary/90 border border-primary shadow-sm disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Signing in...</span>
                  </>
                ) : (
                  mfaToken ? 'Verify and sign in' : 'Sign in'
                )}
              </button>
            </form>

            <div className="text-sm text-muted-foreground mt-2 text-center">
              Don't have an account? <Link href="/signup" className="text-accent hover:underline">Sign up</Link>
            </div>
            <div className="text-sm text-muted-foreground text-center">
              <Link href="/forgot-password" className="text-accent hover:underline">Forgot your password?</Link>
            </div>
            <div className="text-xs text-muted-foreground mt-4 text-center">
              By using Encypher you agree to our <Link href="/terms" className="underline">Terms of Service</Link>, <Link href="/privacy" className="underline">Privacy</Link>, and Security policies and practices.
            </div>
          </div>
        </div>
      </section>

      <section className="hidden md:flex w-1/2 items-center justify-center bg-background relative overflow-hidden min-h-screen">
        <div className="relative z-10 w-full h-full flex items-center justify-center">
          <div className="w-full h-[80vh] relative">
            <MetadataBackground />
          </div>
        </div>
      </section>
    </main>
  );
}
