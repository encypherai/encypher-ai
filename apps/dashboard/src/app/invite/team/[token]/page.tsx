'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useSession, signIn } from 'next-auth/react';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '@encypher/design-system';
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com/api/v1').replace(/\/$/, '');

interface TeamInviteDetails {
  email: string;
  org_name: string;
  role: string;
  expires_at: string | null;
  status: string;
}

export default function TeamInvitePage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status: sessionStatus } = useSession();
  const token = params.token as string;

  const [invite, setInvite] = useState<TeamInviteDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New account form state
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Fetch invite details (no auth required)
  useEffect(() => {
    async function fetchInvite() {
      try {
        const response = await fetch(`${API_BASE}/org/invites/public/${token}`);
        const data = await response.json();

        if (!response.ok) {
          setError((typeof data.detail === 'string' ? data.detail : null) || 'Invitation not found or expired');
          return;
        }

        setInvite(data.data);
      } catch {
        setError('Failed to load invitation');
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      fetchInvite();
    }
  }, [token]);

  // Case 1: logged-in user whose email matches -- accept via authenticated endpoint
  const handleAcceptLoggedIn = async () => {
    if (!session?.user) return;
    const accessToken = (session.user as any).accessToken;

    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE}/org/members/accept-invite?token=${token}&user_id=${(session.user as any).id}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await response.json();

      if (!response.ok) {
        toast.error((typeof data.detail === 'string' ? data.detail : null) || 'Failed to accept invitation');
        return;
      }

      toast.success('You have joined the organization!');
      router.push('/team');
    } catch {
      toast.error('Failed to accept invitation');
    } finally {
      setSubmitting(false);
    }
  };

  // Case 4: new user -- create account + accept invite in one step
  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE}/org/invites/public/${token}/accept-new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, password }),
      });
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          toast.error('An account with this email already exists. Please sign in to accept the invitation.');
        } else {
          toast.error((typeof data.detail === 'string' ? data.detail : null) || 'Failed to create account');
        }
        return;
      }

      toast.success('Account created! Signing you in...');

      // Auto-login with the credentials
      const result = await signIn('credentials', {
        email: invite?.email,
        password,
        redirect: false,
      });

      if (result?.ok) {
        router.push('/team');
      } else {
        router.push('/auth/login?message=Account created. Please sign in.');
      }
    } catch {
      toast.error('Failed to create account');
    } finally {
      setSubmitting(false);
    }
  };

  // Loading
  if (loading || sessionStatus === 'loading') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-ncs mx-auto mb-4" />
          <p className="text-muted-foreground">Loading invitation...</p>
        </div>
      </div>
    );
  }

  // Error / not found
  if (error || !invite) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">Invitation Not Found</h2>
            <p className="text-muted-foreground mb-6">{error || 'This invitation may have expired or been cancelled.'}</p>
            <Button variant="primary" onClick={() => router.push('/')}>Go to Dashboard</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isLoggedIn = !!session?.user;
  const emailMatches = isLoggedIn && session.user.email?.toLowerCase() === invite.email.toLowerCase();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 py-4">
        <div className="max-w-7xl mx-auto px-4">
          <Link href="/">
            <Image
              src="/assets/wordmark-navy-nobg.svg"
              alt="Encypher"
              width={140}
              height={36}
              className="h-8 w-auto"
              priority
            />
          </Link>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center pb-2">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-ncs/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <CardTitle className="text-2xl">You&apos;re Invited!</CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="text-center">
              <p className="text-muted-foreground">You have been invited to join</p>
              <p className="text-xl font-bold text-delft-blue dark:text-white mt-1">{invite.org_name}</p>
              <p className="text-sm text-muted-foreground mt-2">
                as a <span className="font-medium capitalize">{invite.role}</span>
              </p>
            </div>

            <div className="border-t border-border pt-6">
              {/* Case 1: logged in, email matches -- one-click accept */}
              {isLoggedIn && emailMatches && (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground text-center">
                    Signed in as <span className="font-medium">{session.user.email}</span>
                  </p>
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={handleAcceptLoggedIn}
                    disabled={submitting}
                  >
                    {submitting ? 'Joining...' : 'Accept Invitation'}
                  </Button>
                </div>
              )}

              {/* Case 2: logged in, wrong email */}
              {isLoggedIn && !emailMatches && (
                <div className="space-y-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-800">
                      You are signed in as <span className="font-medium">{session.user.email}</span>,
                      but this invitation was sent to <span className="font-medium">{invite.email}</span>.
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => signIn(undefined, { callbackUrl: `/invite/team/${token}` })}
                  >
                    Sign in with {invite.email}
                  </Button>
                </div>
              )}

              {/* Case 3: not logged in -- show sign-in (handles existing users) */}
              {!isLoggedIn && (
                <div className="space-y-6">
                  {/* Always offer sign-in for existing users */}
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground text-center">
                      Already have an account?
                    </p>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => signIn(undefined, { callbackUrl: `/invite/team/${token}` })}
                    >
                      Sign In
                    </Button>
                  </div>

                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-border" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-background px-2 text-muted-foreground">or create account</span>
                    </div>
                  </div>

                  {/* Case 4: new user registration form */}
                  <form onSubmit={handleCreateAccount} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">Email</label>
                      <Input type="email" value={invite.email} disabled className="bg-muted" />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">Your Name</label>
                      <Input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Jane Smith"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">Password</label>
                      <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="At least 8 characters"
                        required
                        minLength={8}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">Confirm Password</label>
                      <Input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm your password"
                        required
                      />
                    </div>

                    <Button
                      type="submit"
                      variant="primary"
                      className="w-full"
                      disabled={submitting || !name || !password || !confirmPassword}
                    >
                      {submitting ? 'Creating Account...' : 'Create Account & Join'}
                    </Button>

                    <p className="text-xs text-muted-foreground text-center">
                      By creating an account, you agree to our{' '}
                      <a href="https://encypher.com/terms" className="text-blue-ncs hover:underline">Terms of Service</a>
                      {' '}and{' '}
                      <a href="https://encypher.com/privacy" className="text-blue-ncs hover:underline">Privacy Policy</a>
                    </p>
                  </form>
                </div>
              )}
            </div>

            {invite.expires_at && (
              <p className="text-xs text-muted-foreground text-center">
                This invitation expires on {new Date(invite.expires_at).toLocaleDateString()}
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
