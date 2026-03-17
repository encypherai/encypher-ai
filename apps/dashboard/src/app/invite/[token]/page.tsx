'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useSession, signIn } from 'next-auth/react';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '@encypher/design-system';
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';

interface InvitationDetails {
  valid: boolean;
  status: string;
  email: string;
  role: string;
  organization_name: string;
  organization_id: string;
  inviter_name: string;
  message?: string;
  expires_at: string;
  user_exists: boolean;
  tier?: string | null;
  trial_months?: number | null;
}

export default function InvitationPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status: sessionStatus } = useSession();
  const token = params.token as string;

  const [invitation, setInvitation] = useState<InvitationDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New account form state
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Fetch invitation details
  useEffect(() => {
    async function fetchInvitation() {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/organizations/invitations/${token}`
        );
        const data = await response.json();

        if (!response.ok) {
          setError(data.detail || 'Invitation not found');
          return;
        }

        setInvitation(data.data);
      } catch (err) {
        setError('Failed to load invitation');
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      fetchInvitation();
    }
  }, [token]);

  // Handle accepting invitation for logged-in users
  const handleAcceptLoggedIn = async () => {
    if (!session?.user) return;

    const accessToken = (session.user as any).accessToken;

    setSubmitting(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/organizations/invitations/${token}/accept`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.detail || 'Failed to accept invitation');
        return;
      }

      toast.success('Successfully joined the organization!');
      router.push('/');
    } catch (err) {
      toast.error('Failed to accept invitation');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle creating new account and accepting
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
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/organizations/invitations/${token}/accept-new`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name, password }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.detail || 'Failed to create account');
        return;
      }

      toast.success('Account created! Signing you in...');

      // Sign in with the new credentials
      const result = await signIn('credentials', {
        email: invitation?.email,
        password: password,
        redirect: false,
      });

      if (result?.ok) {
        router.push('/');
      } else {
        // If auto-login fails, redirect to login page
        router.push('/auth/login?message=Account created. Please sign in.');
      }
    } catch (err) {
      toast.error('Failed to create account');
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (loading || sessionStatus === 'loading') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-ncs mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading invitation...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !invitation) {
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
            <Button variant="primary" onClick={() => router.push('/')}>
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Invalid/expired invitation
  if (!invitation.valid) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-yellow-100 flex items-center justify-center">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">Invitation {invitation.status}</h2>
            <p className="text-muted-foreground mb-6">
              {invitation.status === 'expired'
                ? 'This invitation has expired. Please ask the team admin to send a new one.'
                : invitation.status === 'accepted'
                ? 'This invitation has already been accepted.'
                : 'This invitation is no longer valid.'}
            </p>
            <Button variant="primary" onClick={() => router.push('/')}>
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Check if logged-in user's email matches invitation
  const isLoggedIn = !!session?.user;
  const emailMatches = isLoggedIn && session.user.email?.toLowerCase() === invitation.email.toLowerCase();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 py-4">
        <div className="max-w-7xl mx-auto px-4">
          <Link href="/">
            <Image
              src="/assets/encypher_full_nobg.png"
              alt="Encypher"
              width={140}
              height={36}
              className="h-8 w-auto"
              priority
            />
          </Link>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center pb-2">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-ncs/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <CardTitle className="text-2xl">You're Invited!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Invitation details */}
            <div className="text-center">
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{invitation.inviter_name}</span> has invited you to join
              </p>
              <p className="text-xl font-bold text-delft-blue dark:text-white mt-1">{invitation.organization_name}</p>
              <p className="text-sm text-muted-foreground mt-2">
                as a <span className="font-medium capitalize">{invitation.role}</span>
              </p>
              {(invitation.tier || invitation.trial_months) && (
                <p className="text-sm text-muted-foreground mt-2">
                  Trial:{' '}
                  {invitation.tier
                    ? invitation.tier.charAt(0).toUpperCase() + invitation.tier.slice(1)
                    : 'Tier pending'}
                  {invitation.trial_months
                    ? ` · ${invitation.trial_months} month${invitation.trial_months === 1 ? '' : 's'}`
                    : ''}
                </p>
              )}
            </div>

            {invitation.message && (
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-sm text-muted-foreground italic">"{invitation.message}"</p>
              </div>
            )}

            <div className="border-t border-border pt-6">
              {/* Case 1: User is logged in with matching email */}
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

              {/* Case 2: User is logged in but with different email */}
              {isLoggedIn && !emailMatches && (
                <div className="space-y-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-800">
                      You're signed in as <span className="font-medium">{session.user.email}</span>,
                      but this invitation was sent to <span className="font-medium">{invitation.email}</span>.
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => signIn()}
                  >
                    Sign in with {invitation.email}
                  </Button>
                </div>
              )}

              {/* Case 3: User not logged in, account exists */}
              {!isLoggedIn && invitation.user_exists && (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground text-center">
                    Sign in to accept this invitation
                  </p>
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={() => signIn(undefined, { callbackUrl: `/invite/${token}` })}
                  >
                    Sign In
                  </Button>
                </div>
              )}

              {/* Case 4: User not logged in, no account - show signup form */}
              {!isLoggedIn && !invitation.user_exists && (
                <form onSubmit={handleCreateAccount} className="space-y-4">
                  <p className="text-sm text-muted-foreground text-center">
                    Create your account to join
                  </p>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">Email</label>
                    <Input
                      type="email"
                      value={invitation.email}
                      disabled
                      className="bg-muted"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">Your Name</label>
                    <Input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="John Doe"
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
                    <a href="https://encypherai.com/terms" className="text-blue-ncs hover:underline">Terms of Service</a>
                    {' '}and{' '}
                    <a href="https://encypherai.com/privacy" className="text-blue-ncs hover:underline">Privacy Policy</a>
                  </p>
                </form>
              )}
            </div>

            {/* Expiration notice */}
            <p className="text-xs text-muted-foreground text-center">
              This invitation expires on {new Date(invitation.expires_at).toLocaleDateString()}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
