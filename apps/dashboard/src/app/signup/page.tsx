'use client';

import { Button, Input } from '@encypher/design-system';
import { Suspense, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { signIn } from 'next-auth/react';
import MetadataBackground from '../../components/hero/MetadataBackground';

const LOGO_COLOR = '/assets/encypher_full_logo_color.svg';
const LOGO_WHITE = '/assets/encypher_full_logo_white.svg';

const getApiBase = () => {
  return (
    process.env.NEXT_PUBLIC_API_URL ||
    (process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000/api/v1'
      : 'https://api.encypherai.com/api/v1')
  );
};

const NAME_URL_REGEX = /(https?:\/\/|www\.)/i;
const HTML_TAG_REGEX = /<[^>]*>/g;

const sanitizeName = (value: string) => value.replace(HTML_TAG_REGEX, '').trim();

function SignupPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');

  const source = searchParams.get('source') || '';
  const extensionId = searchParams.get('extensionId') || '';
  const callbackUrl = searchParams.get('callbackUrl') || '/';

  const loginHref = useMemo(() => {
    const params = new URLSearchParams();
    if (source) params.set('source', source);
    if (extensionId) params.set('extensionId', extensionId);
    if (callbackUrl) params.set('callbackUrl', callbackUrl);
    const query = params.toString();
    return query ? `/login?${query}` : '/login';
  }, [callbackUrl, extensionId, source]);

  const handleNameBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    // TEAM_115: sanitize on blur using the latest input value.
    const sanitizedName = sanitizeName(event.target.value);
    if (sanitizedName !== formData.name) {
      setFormData((prev) => ({ ...prev, name: sanitizedName }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const form = new FormData(e.currentTarget as HTMLFormElement);
    const rawName = String(form.get('name') ?? formData.name);
    const rawEmail = String(form.get('email') ?? formData.email);
    const rawPassword = String(form.get('password') ?? formData.password);
    const rawConfirmPassword = String(form.get('confirmPassword') ?? formData.confirmPassword);

    const sanitizedName = sanitizeName(rawName);
    if (!sanitizedName) {
      setError('Full name is required');
      return;
    }

    if (NAME_URL_REGEX.test(sanitizedName)) {
      setError('Name cannot contain URLs');
      return;
    }

    if (sanitizedName !== formData.name) {
      setFormData((prev) => ({ ...prev, name: sanitizedName }));
    } else if (
      rawName !== formData.name ||
      rawEmail !== formData.email ||
      rawPassword !== formData.password ||
      rawConfirmPassword !== formData.confirmPassword
    ) {
      setFormData({
        name: rawName,
        email: rawEmail,
        password: rawPassword,
        confirmPassword: rawConfirmPassword,
      });
    }

    // Validation
    if (rawPassword !== rawConfirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (rawPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      // Call API Gateway signup (SRF)
      const apiBase = getApiBase().replace(/\/$/, '');
      const res = await fetch(`${apiBase}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: sanitizedName,
          email: rawEmail,
          password: rawPassword,
        }),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        // Show success state with email verification notice
        setRegisteredEmail(rawEmail);
        setSuccess(true);
      } else {
        setError(data.detail || data.message || data.error?.message || 'Failed to create account');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Success state - show email verification notice
  if (success) {
    return (
      <main className="flex min-h-screen bg-background">
        <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen">
          <div className="w-full max-w-md rounded-2xl bg-card shadow-2xl border border-border p-8 flex flex-col gap-6">
            <Link href="/" className="inline-flex">
              <Image src={LOGO_COLOR} alt="Encypher" width={160} height={40} className="h-9 w-auto object-contain dark:hidden" priority />
              <Image src={LOGO_WHITE} alt="Encypher" width={160} height={40} className="h-9 w-auto object-contain hidden dark:block" priority />
            </Link>
            <div className="w-14 h-14 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-card-foreground mb-1" data-testid="signup-success-title">Check your email</h1>
              <p className="text-sm text-muted-foreground">
                We&apos;ve sent a verification link to{' '}
                <span className="font-semibold text-foreground">{registeredEmail}</span>
              </p>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <ol className="text-sm text-foreground/80 space-y-1.5 list-decimal list-inside">
                <li>Open your email inbox</li>
                <li>Click the verification link</li>
                <li>You&apos;ll be automatically signed in</li>
              </ol>
            </div>
            <Button variant="primary" size="lg" fullWidth onClick={() => router.push(loginHref)}>
              Go to sign in
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              Didn&apos;t receive it? Check spam or{' '}
              <button className="text-accent hover:underline" onClick={() => { setSuccess(false); setError(''); }}>
                try again
              </button>
            </p>
          </div>
        </section>
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

  return (
    <main className="flex min-h-screen bg-background">
      {/* Left panel — form */}
      <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen">
        <div className="w-full max-w-md rounded-2xl bg-card shadow-2xl border border-border p-8 flex flex-col gap-6">
          <Link href="/" className="inline-flex">
            <Image src={LOGO_COLOR} alt="Encypher" width={160} height={40} className="h-9 w-auto object-contain dark:hidden" priority />
            <Image src={LOGO_WHITE} alt="Encypher" width={160} height={40} className="h-9 w-auto object-contain hidden dark:block" priority />
          </Link>

          <div>
            <h1 className="text-2xl font-bold text-card-foreground mb-1">Create your account</h1>
            <p className="text-sm text-muted-foreground">Sign up for Encypher and unlock secure, metadata-powered AI workflows.</p>
          </div>

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
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              <span className="text-base font-medium">GitHub</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">or sign up with</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg text-sm" role="alert" data-testid="signup-error">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
                <span>{error}</span>
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-foreground mb-1.5">Full name</label>
              <Input id="name" name="name" type="text" placeholder="Jane Smith" value={formData.name} onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))} onBlur={handleNameBlur} required disabled={loading} />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <Input id="email" name="email" type="email" placeholder="you@example.com" value={formData.email} onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))} required disabled={loading} />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1.5">Password</label>
              <Input id="password" name="password" type="password" placeholder="••••••••" value={formData.password} onChange={(e) => setFormData((prev) => ({ ...prev, password: e.target.value }))} required disabled={loading} />
              <p className="text-xs text-muted-foreground mt-1">At least 8 characters</p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-foreground mb-1.5">Confirm password</label>
              <Input id="confirmPassword" name="confirmPassword" type="password" placeholder="••••••••" value={formData.confirmPassword} onChange={(e) => setFormData((prev) => ({ ...prev, confirmPassword: e.target.value }))} required disabled={loading} />
            </div>

            <Button type="submit" variant="primary" size="lg" fullWidth loading={loading}>
              Create account
            </Button>
          </form>

          <div className="text-sm text-muted-foreground text-center">
            Already have an account?{' '}
            <Link href={loginHref} className="font-semibold text-accent hover:underline">Sign in</Link>
          </div>

          <div className="text-xs text-muted-foreground text-center">
            By using Encypher you agree to our{' '}
            <Link href="https://encypherai.com/terms" className="underline">Terms of Service</Link>,{' '}
            <Link href="https://encypherai.com/privacy" className="underline">Privacy</Link>, and Security policies and practices.
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

export default function SignupPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen bg-background">
          <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen">
            <div className="w-full max-w-md rounded-2xl bg-card border border-border p-8">
              <div className="h-9 w-36 bg-muted rounded animate-pulse mb-8" />
              <div className="h-8 w-48 bg-muted rounded animate-pulse mb-2" />
              <div className="h-4 w-64 bg-muted rounded animate-pulse" />
            </div>
          </section>
          <section className="hidden md:flex w-1/2 bg-background relative overflow-hidden min-h-screen">
            <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue opacity-80" />
          </section>
        </main>
      }
    >
      <SignupPageContent />
    </Suspense>
  );
}
