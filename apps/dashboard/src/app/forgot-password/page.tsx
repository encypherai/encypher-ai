'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Input, Button } from '@encypher/design-system';
import MetadataBackground from '../../components/hero/MetadataBackground';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to send reset email');
      }

      setSuccess(true);
    } catch {
      // Don't reveal if email exists or not for security
      setSuccess(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen bg-background">
      <section className="w-full lg:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue opacity-60" />
        <div className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl border border-border p-8 relative z-10">
          <div className="flex flex-col gap-6">
            {success ? (
              <>
                {/* Success State */}
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h1 className="text-2xl font-bold text-card-foreground mb-2">Check your email</h1>
                  <p className="text-muted-foreground mb-6">
                    If an account exists for <strong>{email}</strong>, we&apos;ve sent password reset instructions.
                  </p>
                  <p className="text-sm text-muted-foreground mb-6">
                    Didn&apos;t receive the email? Check your spam folder or try again.
                  </p>
                </div>

                <div className="space-y-3">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => {
                      setSuccess(false);
                      setEmail('');
                    }}
                  >
                    Try another email
                  </Button>
                  <Link href="/login" className="block">
                    <Button variant="primary" className="w-full">
                      Back to sign in
                    </Button>
                  </Link>
                </div>
              </>
            ) : (
              <>
                {/* Form State */}
                <div>
                  <Link href="/login" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to sign in
                  </Link>
                  <h1 className="text-2xl font-bold text-card-foreground mb-1">Reset your password</h1>
                  <p className="text-sm text-muted-foreground">
                    Enter your email address and we&apos;ll send you instructions to reset your password.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {error && (
                    <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg text-sm">
                      {error}
                    </div>
                  )}

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
                      Email address
                    </label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={loading}
                      autoFocus
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    className="w-full"
                    disabled={loading || !email}
                  >
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Sending...
                      </span>
                    ) : (
                      'Send reset instructions'
                    )}
                  </Button>
                </form>

                <div className="text-sm text-muted-foreground text-center">
                  Remember your password?{' '}
                  <Link href="/login" className="text-accent hover:underline">
                    Sign in
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="hidden lg:flex w-1/2 items-center justify-center relative overflow-hidden min-h-screen" style={{ background: 'linear-gradient(135deg, #1a2332 0%, #1e3a5f 40%, #1b2f50 100%)' }}>
        <div className="relative z-10 w-full h-full flex items-center justify-center">
          <div className="w-full h-[80vh] relative">
            <MetadataBackground />
          </div>
        </div>
      </section>
    </main>
  );
}
