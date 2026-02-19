'use client';

import { Button, Input } from '@encypher/design-system';
import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { signIn } from 'next-auth/react';
import Image from 'next/image';
import apiClient from '../../lib/api';

// Note: API_BASE not used directly in login - auth goes through NextAuth
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import MetadataBackground from '../../components/hero/MetadataBackground';

// Canonical SVG logos
const LOGO_COLOR = '/assets/encypher_full_logo_color.svg';
const LOGO_WHITE = '/assets/encypher_full_logo_white.svg';

function LoginPageContent() {
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passkeyLoading, setPasskeyLoading] = useState(false);
  const autoAuthTriggeredRef = useRef(false);

  const source = searchParams.get('source') || '';
  const extensionId = searchParams.get('extensionId') || '';
  const provider = (searchParams.get('provider') || '').toLowerCase();

  const callbackUrl = useMemo(() => {
    const raw = searchParams.get('callbackUrl') || '/';
    try {
      const parsed = new URL(raw, 'http://local.app');
      if (parsed.origin !== 'http://local.app' || !parsed.pathname.startsWith('/')) {
        return '/';
      }
      return `${parsed.pathname}${parsed.search}${parsed.hash}` || '/';
    } catch {
      return '/';
    }
  }, [searchParams]);

  const signupHref = useMemo(() => {
    const params = new URLSearchParams();
    if (source) params.set('source', source);
    if (extensionId) params.set('extensionId', extensionId);
    if (callbackUrl) params.set('callbackUrl', callbackUrl);
    const query = params.toString();
    return query ? `/signup?${query}` : '/signup';
  }, [callbackUrl, extensionId, source]);

  useEffect(() => {
    if (autoAuthTriggeredRef.current) return;
    if (provider !== 'google' && provider !== 'github') return;
    autoAuthTriggeredRef.current = true;
    signIn(provider, { callbackUrl });
  }, [callbackUrl, provider]);

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
        callbackUrl,
      });

      if (result?.error) {
        throw new Error(result.error);
      }
      window.location.href = callbackUrl;
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
        callbackUrl,
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
        window.location.href = callbackUrl;
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
      {/* Left panel — form */}
      <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen">
        <div className="w-full max-w-md rounded-2xl bg-card shadow-2xl border border-border p-8 flex flex-col gap-6">
          {/* Logo */}
          <Link href="/" className="inline-flex mb-2">
            <Image
              src={LOGO_COLOR}
              alt="Encypher"
              width={160}
              height={40}
              className="h-9 w-auto object-contain dark:hidden"
              priority
            />
            <Image
              src={LOGO_WHITE}
              alt="Encypher"
              width={160}
              height={40}
              className="h-9 w-auto object-contain hidden dark:block"
              priority
            />
          </Link>

          <div>
            <h1 className="text-2xl font-bold text-card-foreground mb-1">Welcome back</h1>
            <p className="text-sm text-muted-foreground">Sign in to your Encypher account</p>
          </div>

          {/* OAuth buttons */}
          <div className="flex flex-row gap-3 w-full">
            <button
              type="button"
              disabled={loading}
              onClick={() => signIn('google', { callbackUrl })}
              className="flex items-center justify-center gap-2 flex-1 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
              style={{ boxShadow: '0 2px 10px 0 #4285F4' }}
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              <span className="text-base font-medium">Google</span>
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => signIn('github', { callbackUrl })}
              className="flex items-center justify-center gap-2 flex-1 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
              style={{ boxShadow: '0 2px 10px 0 #2a87c4' }}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.83-.729.83-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              <span className="text-base font-medium">GitHub</span>
            </button>
          </div>

          <Button
            type="button"
            variant="outline"
            fullWidth
            disabled={loading || passkeyLoading}
            onClick={handlePasskeyLogin}
            loading={passkeyLoading}
          >
            {passkeyLoading ? 'Waiting for passkey…' : 'Sign in with passkey'}
          </Button>

          <div className="flex items-center gap-2">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">or sign in with</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg text-sm" role="alert">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <Input id="email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={loading} />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="block text-sm font-medium text-foreground">Password</label>
                <Link href="/forgot-password" className="text-xs text-accent hover:underline">Forgot password?</Link>
              </div>
              <Input id="password" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={loading} />
            </div>

            {mfaToken && (
              <div>
                <label htmlFor="mfa-code" className="block text-sm font-medium text-foreground mb-1.5">Authentication code</label>
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

            <Button type="submit" variant="primary" size="lg" fullWidth loading={loading}>
              {mfaToken ? 'Verify and sign in' : 'Sign in'}
            </Button>
          </form>

          <div className="flex flex-col items-center gap-1 text-sm text-muted-foreground">
            <span>Don&apos;t have an account?{' '}
              <Link href={signupHref} className="font-semibold text-accent hover:underline">Sign up</Link>
            </span>
          </div>

          <div className="text-xs text-muted-foreground text-center">
            By using Encypher you agree to our{' '}
            <Link href="/terms" className="underline">Terms of Service</Link>,{' '}
            <Link href="/privacy" className="underline">Privacy</Link>, and Security policies and practices.
          </div>
        </div>
      </section>

      {/* Right panel — animation only, matching marketing site */}
      <section className="hidden md:flex w-1/2 items-center justify-center bg-background relative overflow-hidden min-h-screen">
        <div className="absolute inset-0 w-full h-full">
          <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue opacity-80 z-0" />
          <div className="relative z-10 w-full h-full">
            <MetadataBackground />
          </div>
        </div>
      </section>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen">
          <section className="w-full md:w-1/2 flex flex-col justify-center px-8 py-12 bg-white dark:bg-gray-950">
            <div className="w-full max-w-sm mx-auto">
              <div className="h-9 w-36 bg-gray-100 dark:bg-gray-800 rounded animate-pulse mb-10" />
              <div className="h-8 w-48 bg-gray-100 dark:bg-gray-800 rounded animate-pulse mb-2" />
              <div className="h-4 w-64 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
            </div>
          </section>
          <section className="hidden md:block md:w-1/2 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue" />
        </main>
      }
    >
      <LoginPageContent />
    </Suspense>
  );
}
