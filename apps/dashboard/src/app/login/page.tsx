'use client';

import { Button, Input } from '@encypher/design-system';
import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { signIn } from 'next-auth/react';
import Image from 'next/image';
import apiClient from '../../lib/api';
import TurnstileWidget from '../../components/security/TurnstileWidget';

// Note: API_BASE not used directly in login - auth goes through NextAuth
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import MetadataBackground from '../../components/hero/MetadataBackground';
import { ThemeProvider as NextThemesProvider } from 'next-themes';

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
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
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
      const refreshToken = (authData as any)?.refresh_token as string | undefined;
      if (!accessToken) {
        throw new Error('Passkey authentication did not return a session token.');
      }

      const result = await signIn('credentials', {
        email,
        password: `__TOKEN__${accessToken}`,
        refreshToken,
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
        turnstileToken: turnstileToken || undefined,
        redirect: false,
        callbackUrl,
      });

      if (result?.error) {
        const decodedError = decodeURIComponent(result.error || '');
        if (decodedError.startsWith('MFA_REQUIRED:')) {
          setMfaToken(decodedError.replace('MFA_REQUIRED:', ''));
          setError('Enter your authentication code to finish signing in.');
          setLoading(false);
          return;
        }
        // NextAuth passes the error message from authorize() in result.error
        setError(decodedError === 'CredentialsSignin' ? 'Invalid email or password' : decodedError);
        setTurnstileToken(null);
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
      setTurnstileToken(null);
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen bg-background">
      {/* Left panel -- form */}
      <section className="w-full lg:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen">
        <div className="w-full max-w-md rounded-2xl bg-card shadow-2xl border border-border p-6 sm:p-8 flex flex-col gap-6">
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

          {/* OAuth + Passkey buttons */}
          <div className="flex flex-row gap-3 w-full">
            <button
              type="button"
              disabled={loading}
              onClick={() => signIn('google', { callbackUrl })}
              aria-label="Sign in with Google"
              className="flex items-center justify-center gap-2 flex-1 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
            >
              <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              <span className="text-sm font-medium hidden sm:inline">Google</span>
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => signIn('github', { callbackUrl })}
              aria-label="Sign in with GitHub"
              className="flex items-center justify-center gap-2 flex-1 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
            >
              <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.83-.729.83-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              <span className="text-sm font-medium hidden sm:inline">GitHub</span>
            </button>
            <button
              type="button"
              disabled={loading || passkeyLoading}
              onClick={handlePasskeyLogin}
              aria-label="Sign in with Passkey"
              className="flex items-center justify-center gap-2 flex-1 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm"
            >
              <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              <span className="text-sm font-medium hidden sm:inline">{passkeyLoading ? 'Waiting...' : 'Passkey'}</span>
            </button>
          </div>

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

            <TurnstileWidget
              onVerify={setTurnstileToken}
              onExpire={() => setTurnstileToken(null)}
              onError={() => setTurnstileToken(null)}
              action="login"
            />

            <Button type="submit" variant="primary" size="lg" fullWidth loading={loading} disabled={!turnstileToken}>
              {mfaToken ? 'Verify and sign in' : 'Sign in'}
            </Button>
          </form>

          <div className="flex flex-col items-center gap-2 text-sm">
            <span className="text-muted-foreground">Don&apos;t have an account?</span>
            <Link
              href={signupHref}
              className="w-full flex items-center justify-center py-2.5 px-4 rounded-lg font-semibold text-accent border border-accent/40 hover:bg-accent/10 transition text-sm"
            >
              Create an account
            </Link>
          </div>

          <div className="text-xs text-muted-foreground text-center">
            By using Encypher you agree to our{' '}
            <Link href="https://encypher.com/terms" className="underline">Terms of Service</Link>,{' '}
            <Link href="https://encypher.com/privacy" className="underline">Privacy</Link>, and Security policies and practices.
          </div>
        </div>
      </section>

      {/* Right panel -- brand content over animated background */}
      <section className="hidden lg:flex w-1/2 items-center justify-center relative overflow-hidden min-h-screen" style={{ background: 'linear-gradient(135deg, #1a2332 0%, #1e3a5f 40%, #1b2f50 100%)' }}>
        <div className="absolute inset-0 w-full h-full">
          <NextThemesProvider forcedTheme="dark" attribute="class">
            <MetadataBackground />
          </NextThemesProvider>
        </div>
        {/* Quiet zone: frosted-glass overlay behind text content */}
        <div className="relative z-20 max-w-md px-12 text-white">
          <div className="rounded-2xl bg-black/20 backdrop-blur-md border border-white/10 p-8">
            <div className="mb-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-xs font-medium mb-6">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Built on the C2PA standard
              </div>
              <h2 className="text-4xl font-extrabold leading-tight mb-4 tracking-tight">
                Your content.<br />Your rights.<br />Verifiable anywhere.
              </h2>
              <p className="text-white/70 text-sm leading-relaxed">
                The provenance infrastructure that publishers and AI platforms trust.
              </p>
            </div>
            <div className="space-y-4">
              {[
                { icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', text: 'Prove who published what, and when' },
                { icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z', text: 'Track how content travels across the open web' },
                { icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', text: 'Build trust between publishers and AI platforms' },
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                  </div>
                  <p className="text-sm text-white/90 leading-relaxed">{item.text}</p>
                </div>
              ))}
            </div>
            <div className="mt-10 pt-8 border-t border-white/20">
              <p className="text-xs text-white/50 uppercase tracking-wider font-medium mb-3">Trusted standard</p>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Coalition for Content Provenance</p>
                  <p className="text-xs text-white/60">C2PA Text Provenance Task Force</p>
                </div>
              </div>
            </div>
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
          <section className="w-full lg:w-1/2 flex flex-col justify-center px-8 py-12 bg-white dark:bg-gray-950">
            <div className="w-full max-w-sm mx-auto">
              <div className="h-9 w-36 bg-gray-100 dark:bg-gray-800 rounded animate-pulse mb-10" />
              <div className="h-8 w-48 bg-gray-100 dark:bg-gray-800 rounded animate-pulse mb-2" />
              <div className="h-4 w-64 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
            </div>
          </section>
          <section className="hidden lg:block lg:w-1/2" style={{ background: 'linear-gradient(135deg, #1a2332 0%, #1e3a5f 40%, #1b2f50 100%)' }} />
        </main>
      }
    >
      <LoginPageContent />
    </Suspense>
  );
}
