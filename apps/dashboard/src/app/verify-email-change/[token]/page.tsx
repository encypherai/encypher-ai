'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@encypher/design-system';
import MetadataBackground from '../../../components/hero/MetadataBackground';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com/api/v1').replace(/\/$/, '');

type VerificationStatus = 'verifying' | 'success' | 'error' | 'expired';

export default function VerifyEmailChangePage() {
  const params = useParams();
  const token = params.token as string;

  const [status, setStatus] = useState<VerificationStatus>('verifying');
  const [error, setError] = useState('');
  const [newEmail, setNewEmail] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setError('Invalid verification link');
      return;
    }

    const verifyEmailChange = async () => {
      try {
        const response = await fetch(`${API_BASE}/auth/verify-email-change`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (!response.ok) {
          if (response.status === 410 || (typeof data.detail === 'string' && data.detail.includes('expired'))) {
            setStatus('expired');
          } else {
            setStatus('error');
            setError((typeof data.detail === 'string' ? data.detail : null) || 'Failed to verify email change');
          }
          return;
        }

        setNewEmail(data.new_email || data.email || '');
        setStatus('success');
      } catch {
        setStatus('error');
        setError('An unexpected error occurred. Please try again.');
      }
    };

    verifyEmailChange();
  }, [token]);

  return (
    <main className="flex min-h-screen bg-background">
      <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue/20 via-transparent to-blue-ncs/10" />

        <div className="relative z-10 w-full max-w-md">
          <div className="bg-card rounded-xl shadow-lg border border-border p-8">
            {status === 'verifying' && (
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-card-foreground mb-2">Verifying your email</h1>
                <p className="text-muted-foreground">Please wait while we verify your new email address...</p>
              </div>
            )}

            {status === 'success' && (
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-card-foreground mb-2">Email Changed Successfully!</h1>
                <p className="text-muted-foreground mb-6">
                  Your email has been updated to <strong className="text-foreground">{newEmail}</strong>.
                  You can now use this email to sign in.
                </p>
                <Link href="/login">
                  <Button variant="primary" className="w-full">
                    Sign in with new email
                  </Button>
                </Link>
              </div>
            )}

            {status === 'expired' && (
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-card-foreground mb-2">Link Expired</h1>
                <p className="text-muted-foreground mb-6">
                  This verification link has expired. Email change links are valid for 24 hours.
                  Please request a new email change from your settings.
                </p>
                <div className="space-y-3">
                  <Link href="/settings">
                    <Button variant="primary" className="w-full">
                      Go to Settings
                    </Button>
                  </Link>
                  <Link href="/">
                    <Button variant="outline" className="w-full">
                      Back to Dashboard
                    </Button>
                  </Link>
                </div>
              </div>
            )}

            {status === 'error' && (
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-card-foreground mb-2">Verification Failed</h1>
                <p className="text-muted-foreground mb-6">{error}</p>
                <div className="space-y-3">
                  <Link href="/settings">
                    <Button variant="primary" className="w-full">
                      Go to Settings
                    </Button>
                  </Link>
                  <Link href="/support">
                    <Button variant="outline" className="w-full">
                      Contact Support
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            Need help?{' '}
            <Link href="/support" className="text-blue-ncs hover:underline">
              Contact Support
            </Link>
          </p>
        </div>
      </section>

      {/* Right side - Decorative */}
      <section className="hidden md:flex w-1/2 bg-gradient-to-br from-columbia-blue via-blue-ncs/30 to-delft-blue/20 items-center justify-center relative overflow-hidden">
        <MetadataBackground />
      </section>
    </main>
  );
}
