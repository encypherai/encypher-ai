'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Input, Button } from '@encypher/design-system';
import MetadataBackground from '../../../components/hero/MetadataBackground';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com/api/v1').replace(/\/$/, '');

export default function ResetPasswordPage() {
  const params = useParams();
  const token = params.token as string;

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Validate token on mount
  useEffect(() => {
    const validateToken = async () => {
      try {
        const response = await fetch(`${API_BASE}/auth/validate-reset-token?token=${token}`);
        setTokenValid(response.ok);
      } catch {
        setTokenValid(false);
      } finally {
        setValidating(false);
      }
    };

    if (token) {
      validateToken();
    } else {
      setValidating(false);
      setTokenValid(false);
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to reset password');
      }

      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  // Password strength indicator
  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return { strength: 0, label: '', color: '' };
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;

    if (strength <= 2) return { strength, label: 'Weak', color: 'bg-red-500' };
    if (strength <= 3) return { strength, label: 'Fair', color: 'bg-yellow-500' };
    if (strength <= 4) return { strength, label: 'Good', color: 'bg-blue-500' };
    return { strength, label: 'Strong', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(password);

  return (
    <main className="flex min-h-screen bg-background">
      <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue opacity-60" />
        <div className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl border border-border p-8 relative z-10">
          <div className="flex flex-col gap-6">
            {validating ? (
              /* Loading State */
              <div className="text-center py-8">
                <div className="w-12 h-12 mx-auto mb-4 border-4 border-blue-ncs border-t-transparent rounded-full animate-spin" />
                <p className="text-muted-foreground">Validating reset link...</p>
              </div>
            ) : !tokenValid ? (
              /* Invalid Token State */
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-card-foreground mb-2">Invalid or expired link</h1>
                <p className="text-muted-foreground mb-6">
                  This password reset link is invalid or has expired. Please request a new one.
                </p>
                <Link href="/forgot-password">
                  <Button variant="primary" className="w-full">
                    Request new reset link
                  </Button>
                </Link>
              </div>
            ) : success ? (
              /* Success State */
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-card-foreground mb-2">Password reset successful</h1>
                <p className="text-muted-foreground mb-6">
                  Your password has been reset. You can now sign in with your new password.
                </p>
                <Link href="/login">
                  <Button variant="primary" className="w-full">
                    Sign in
                  </Button>
                </Link>
              </div>
            ) : (
              /* Form State */
              <>
                <div>
                  <h1 className="text-2xl font-bold text-card-foreground mb-1">Create new password</h1>
                  <p className="text-sm text-muted-foreground">
                    Enter a new password for your account. Make sure it&apos;s at least 8 characters.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {error && (
                    <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg text-sm">
                      {error}
                    </div>
                  )}

                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                      New password
                    </label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter new password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      disabled={loading}
                      autoFocus
                    />
                    {password && (
                      <div className="mt-2">
                        <div className="flex gap-1 mb-1">
                          {[1, 2, 3, 4, 5].map((i) => (
                            <div
                              key={i}
                              className={`h-1 flex-1 rounded-full ${
                                i <= passwordStrength.strength ? passwordStrength.color : 'bg-gray-200'
                              }`}
                            />
                          ))}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Password strength: <span className="font-medium">{passwordStrength.label}</span>
                        </p>
                      </div>
                    )}
                  </div>

                  <div>
                    <label htmlFor="confirmPassword" className="block text-sm font-medium text-foreground mb-2">
                      Confirm new password
                    </label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      placeholder="Confirm new password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      disabled={loading}
                    />
                    {confirmPassword && password !== confirmPassword && (
                      <p className="text-xs text-destructive mt-1">Passwords do not match</p>
                    )}
                    {confirmPassword && password === confirmPassword && (
                      <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Passwords match
                      </p>
                    )}
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    className="w-full"
                    disabled={loading || !password || !confirmPassword || password !== confirmPassword}
                  >
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Resetting...
                      </span>
                    ) : (
                      'Reset password'
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
