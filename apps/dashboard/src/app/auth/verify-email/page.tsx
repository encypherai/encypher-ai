'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { signIn } from 'next-auth/react';
import Link from 'next/link';
import Image from 'next/image';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
} from '@encypher/design-system';

const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com/api/v1').replace(/\/$/, '');

// Canonical SVG logo
const LOGO_WHITE = '/assets/encypher_full_logo_white.svg';

type VerificationState = 'verifying' | 'success' | 'error' | 'logging-in';

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [state, setState] = useState<VerificationState>('verifying');
  const [error, setError] = useState<string>('');
  const [userEmail, setUserEmail] = useState<string>('');

  useEffect(() => {
    if (!token) {
      setState('error');
      setError('No verification token provided. Please check your email link.');
      return;
    }

    verifyEmail(token);
  }, [token]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      setState('verifying');

      const res = await fetch(`${API_BASE}/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: verificationToken }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        setState('error');
        setError(data.detail || data.error?.message || 'Invalid or expired verification token.');
        return;
      }

      // Verification successful - we have tokens for auto-login
      const { access_token, refresh_token, user } = data.data;
      setUserEmail(user?.email || '');

      // Auto-login the user
      setState('logging-in');

      // Use NextAuth to create a session with the credentials
      // We'll sign in with the email and a special flag to indicate we're using tokens
      const signInResult = await signIn('credentials', {
        email: user.email,
        // Pass the access token as the password - our authorize function will detect this
        password: `__TOKEN__${access_token}`,
        refreshToken: refresh_token,
        callbackUrl: '/',
      });

      if (signInResult?.error) {
        // If token-based login fails, show success but ask user to login manually
        setState('success');
      }
    } catch (err) {
      setState('error');
      setError('An error occurred while verifying your email. Please try again.');
      console.error('Verification error:', err);
    }
  };

  const handleGoToDashboard = () => {
    router.push('/');
  };

  const handleResendEmail = () => {
    router.push('/login?resend=true');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link href="/">
            <span className="sr-only">Encypher</span>
            <Image
              src={LOGO_WHITE}
              alt="Encypher"
              width={180}
              height={45}
              className="h-12 w-auto object-contain"
              priority
            />
          </Link>
        </div>

        <Card className="shadow-2xl">
          <CardHeader className="text-center">
            {state === 'verifying' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-ncs animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <CardTitle className="text-2xl">Verifying Your Email</CardTitle>
                <CardDescription>Please wait while we verify your email address...</CardDescription>
              </>
            )}

            {state === 'logging-in' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <CardTitle className="text-2xl text-green-600">Email Verified!</CardTitle>
                <CardDescription>Logging you in automatically...</CardDescription>
              </>
            )}

            {state === 'success' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <CardTitle className="text-2xl text-green-600">Email Verified!</CardTitle>
                <CardDescription>
                  Your email has been verified successfully.
                  {userEmail && <span className="block mt-1 font-medium">{userEmail}</span>}
                </CardDescription>
              </>
            )}

            {state === 'error' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <CardTitle className="text-2xl text-red-600">Verification Failed</CardTitle>
                <CardDescription className="text-red-600/80">{error}</CardDescription>
              </>
            )}
          </CardHeader>

          <CardContent className="space-y-4">
            {state === 'success' && (
              <>
                <p className="text-sm text-muted-foreground text-center">
                  You can now sign in to access your dashboard and start using Encypher.
                </p>
                <Button
                  variant="primary"
                  size="lg"
                  fullWidth
                  onClick={handleGoToDashboard}
                >
                  Go to Dashboard
                </Button>
              </>
            )}

            {state === 'error' && (
              <>
                <p className="text-sm text-muted-foreground text-center">
                  The verification link may have expired or already been used.
                </p>
                <div className="space-y-2">
                  <Button
                    variant="primary"
                    size="lg"
                    fullWidth
                    onClick={handleResendEmail}
                  >
                    Request New Verification Email
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    fullWidth
                    onClick={handleGoToDashboard}
                  >
                    Go to Login
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-white/60">
          <Link href="https://encypher.com" className="hover:text-white">
            ← Back to main site
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center text-white">
          <div className="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full mx-auto mb-4" />
          <p>Loading...</p>
        </div>
      </main>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
