"use client";
import { getProviders, signIn } from "next-auth/react";
import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import MetadataBackground from '@/components/hero/MetadataBackground';
import { SignInForm } from '@/components/auth/SignInForm';
import { SignUpForm } from '@/components/auth/SignUpForm';
import { useToast } from '@/components/ui/use-toast';
import { fetchApi } from '@/lib/api';

// SVGs for Google and GitHub
const GoogleIcon = () => (
  <svg width="22" height="22" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" tabIndex={-1}>
    <title>Sign in with Google</title>
    <g>
      <path d="M44.5 20H24V28.5H36.7C35.2 33.1 30.9 36.1 25.5 36.1C18.7 36.1 13 30.4 13 23.6C13 16.8 18.7 11.1 25.5 11.1C28.6 11.1 31.3 12.2 33.4 14L39.2 8.2C35.6 4.9 30.9 3 25.5 3C14.2 3 5 12.2 5 23.6C5 35 14.2 44.2 25.5 44.2C36.8 44.2 46 35 46 23.6C46 22.2 45.8 21.1 45.5 20Z" fill="#E0E0E0"/>
      <path d="M6.7 14.1L13.8 19.4C15.7 15.3 20.2 11.1 25.5 11.1C28.6 11.1 31.3 12.2 33.4 14L39.2 8.2C35.6 4.9 30.9 3 25.5 3C17.6 3 10.7 7.9 6.7 14.1Z" fill="#F44336"/>
      <path d="M25.5 44.2C30.6 44.2 35.1 42.4 38.5 39.6L32.8 34.2C30.8 35.7 28.3 36.6 25.5 36.6C20.2 36.6 15.7 32.4 13.8 28.3L6.7 33.6C10.7 39.8 17.6 44.2 25.5 44.2Z" fill="#4CAF50"/>
      <path d="M45.5 20H44.5V20H24V28.5H36.7C36 30.7 34.5 32.6 32.8 34.2L38.5 39.6C41.7 36.7 44 31.9 44 26.4C44 24.7 43.8 22.7 43.5 21.5C44.1 20.7 44.5 20 45.5 20Z" fill="#2196F3"/>
    </g>
  </svg>
);
const GitHubIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" tabIndex={-1}>
    <title>Sign in with GitHub</title>
    <path d="M12 2C6.477 2 2 6.484 2 12.021c0 4.426 2.865 8.184 6.839 9.504.5.092.682-.217.682-.482 0-.237-.009-.868-.014-1.703-2.782.605-3.369-1.342-3.369-1.342-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.004.07 1.533 1.032 1.533 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.339-2.22-.253-4.555-1.112-4.555-4.951 0-1.093.39-1.987 1.029-2.687-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.025A9.563 9.563 0 0 1 12 6.844c.85.004 1.705.115 2.504.337 1.909-1.295 2.748-1.025 2.748-1.025.546 1.378.203 2.397.1 2.65.64.7 1.028 1.594 1.028 2.687 0 3.848-2.338 4.695-4.566 4.944.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.746 0 .267.18.577.688.48C19.138 20.2 22 16.447 22 12.021 22 6.484 17.523 2 12 2Z" />
  </svg>
);

const DiscordIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" tabIndex={-1}>
    <title>Sign in with Discord</title>
    <g>
      <path fill="#5865F2" d="M20.317 4.369A19.791 19.791 0 0 0 16.885 3.3a.074.074 0 0 0-.079.037c-.341.607-.722 1.398-.986 2.025a18.313 18.313 0 0 0-5.487 0A12.583 12.583 0 0 0 9.34 3.337a.077.077 0 0 0-.079-.037c-3.432.999-5.432 2.497-5.41 2.489a.064.064 0 0 0-.028.027C.533 8.089-.32 11.63.099 15.106a.08.08 0 0 0 .03.056c2.077 1.527 4.096 2.466 6.081 3.088a.077.077 0 0 0 .084-.027c.469-.646.889-1.329 1.246-2.05a.076.076 0 0 0-.041-.104c-.663-.249-1.294-.549-1.899-.892a.077.077 0 0 1-.008-.128c.127-.096.254-.197.372-.297a.074.074 0 0 1 .077-.01c3.993 1.826 8.317 1.826 12.269 0a.075.075 0 0 1 .078.009c.119.1.245.201.372.297a.077.077 0 0 1-.006.128 12.298 12.298 0 0 1-1.9.892.076.076 0 0 0-.04.105c.36.72.78 1.403 1.246 2.049a.076.076 0 0 0 .084.028c1.986-.622 4.005-1.561 6.083-3.088a.077.077 0 0 0 .03-.055c.5-4.13-.838-7.637-3.548-10.712a.061.061 0 0 0-.027-.028z"/>
      <path fill="#FFF" d="M15.47 13.37c-.789 0-1.441-.724-1.441-1.612 0-.889.637-1.612 1.441-1.612.813 0 1.457.732 1.441 1.612 0 .888-.637 1.612-1.441 1.612zm-6.954 0c-.788 0-1.441-.724-1.441-1.612 0-.889.637-1.612 1.441-1.612.813 0 1.457.732 1.441 1.612 0 .888-.628 1.612-1.441 1.612z"/>
    </g>
  </svg>
);

interface SignInPageProps {
  initialMode?: 'signin' | 'signup';
}

// Loading component to show while the main component is loading
function SignInLoading() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Loading...</h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Please wait while we load the sign-in page.</p>
        </div>
      </div>
    </div>
  );
}

// Map NextAuth error codes to user-friendly messages
const errorMessages: Record<string, string> = {
  OAuthSignin: 'Error starting OAuth sign-in. Please try again or contact support.',
  OAuthCallback: 'Error during OAuth callback. Please try again.',
  OAuthCreateAccount: 'Could not create OAuth account. Please try again.',
  EmailCreateAccount: 'Could not create email account. Please try again.',
  Callback: 'Error during authentication callback.',
  OAuthAccountNotLinked: 'This email is already associated with another account.',
  EmailSignin: 'Error sending verification email.',
  CredentialsSignin: 'Invalid email or password.',
  SessionRequired: 'Please sign in to access this page.',
  Default: 'An authentication error occurred. Please try again.',
};

// Main component that uses client-side hooks
function SignInContent({ initialMode = 'signin' }: SignInPageProps) {
  const { toast } = useToast();
  const searchParams = useSearchParams();
  // Use non-nullable providers state
  const [providers, setProviders] = useState<Record<string, { id: string; name: string }>>({});
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [showRegistrationStatus, setShowRegistrationStatus] = useState(false);

  // Add state for sign-up fields
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupConfirm, setSignupConfirm] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupError, setSignupError] = useState<string | null>(null);
  
  // Email verification state
  const [showEmailNotVerified, setShowEmailNotVerified] = useState(false);
  const [unverifiedEmail, setUnverifiedEmail] = useState('');
  const [resendLoading, setResendLoading] = useState(false);

  // Effect to update mode from URL params or initialMode prop
  useEffect(() => {
    const modeParam = searchParams.get('mode');
    if (modeParam === 'signup') {
      setMode('signup');
    } else if (modeParam === 'signin') {
      setMode('signin');
    } else {
      setMode(initialMode);
    }
  }, [initialMode, searchParams]);

  // Track source for analytics (from URL param like ?source=publishers)
  useEffect(() => {
    const source = searchParams.get('source');
    if (source && typeof window !== 'undefined') {
      // Store source in sessionStorage for analytics tracking after signup
      sessionStorage.setItem('signup_source', source);
    }
  }, [searchParams]);

  // Handle OAuth error from query params (e.g., ?error=OAuthSignin)
  useEffect(() => {
    const errorCode = searchParams.get('error');
    if (errorCode) {
      const errorMessage = errorMessages[errorCode] || errorMessages.Default;
      setError(errorMessage);
      toast({ title: 'Authentication Error', description: errorMessage, variant: 'error' });
      // Clean up URL without reloading
      window.history.replaceState({}, '', '/auth/signin');
    }
  }, [searchParams, toast]);

  // If already signed in, redirect to dashboard
  useEffect(() => {
    if (typeof window !== "undefined") {
      const session = window.localStorage.getItem("next-auth.session-token");
      const dashboardUrl = process.env.NEXT_PUBLIC_DASHBOARD_URL || "https://dashboard.encypherai.com";
      if (session) window.location.href = dashboardUrl;
    }
  }, [router]);

  useEffect(() => {
    // When fetching providers, always set to an object (never null)
    async function fetchProviders() {
      try {
        const response = await getProviders();
        const data = response || {};
        setProviders(data);
      } catch {
        setProviders({});
      }
    }
    fetchProviders();
  }, []);

  const handleCredentialsSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setShowEmailNotVerified(false);
    const dashboardUrl = process.env.NEXT_PUBLIC_DASHBOARD_URL || "https://dashboard.encypherai.com";
    try {
      const res = await signIn('credentials', {
        redirect: false,
        email,
        password,
        callbackUrl: dashboardUrl,
      });
      if (res && !res.error) {
        toast({ title: 'Signed in successfully!', variant: 'success' });
        window.location.href = dashboardUrl;
      } else {
        // Check if error is about email not verified
        const errorMsg = res?.error || '';
        if (errorMsg.toLowerCase().includes('not verified') || errorMsg.toLowerCase().includes('verify')) {
          setShowEmailNotVerified(true);
          setUnverifiedEmail(email);
          setError('Please verify your email before signing in.');
          toast({ title: 'Email not verified', description: 'Please check your inbox for the verification email.', variant: 'error' });
        } else {
          setError('Invalid email or password.');
          toast({ title: 'Sign in failed', description: 'Invalid email or password.', variant: 'error' });
        }
      }
    } catch {
      setError('Network error. Please try again.');
      toast({ title: 'Network error', description: 'Please try again.', variant: 'error' });
    } finally {
      setLoading(false);
    }
  };
  
  // Resend verification email
  const handleResendVerification = async () => {
    if (!unverifiedEmail) return;
    setResendLoading(true);
    try {
      const response = await fetchApi<{ success: boolean }>('/auth/resend-verification', {
        method: 'POST',
        body: JSON.stringify({ email: unverifiedEmail }),
      });
      if (response.success) {
        toast({ title: 'Verification email sent', description: 'Please check your inbox.', variant: 'success' });
      } else {
        toast({ title: 'Failed to send', description: 'Please try again later.', variant: 'error' });
      }
    } catch {
      toast({ title: 'Error', description: 'Failed to resend verification email.', variant: 'error' });
    } finally {
      setResendLoading(false);
    }
  };

  // Sign up handler
  const handleSignUp = async (email: string, password: string, confirm: string) => {
    setSignupError(null);
    if (!email.match(/^[^@\s]+@[^@\s]+\.[^@\s]+$/)) {
      setSignupError('Please enter a valid email address.');
      toast({ title: 'Invalid email', description: 'Please enter a valid email address.', variant: 'error' });
      return;
    }
    if (password.length < 8) {
      setSignupError('Password must be at least 8 characters.');
      toast({ title: 'Weak password', description: 'Password must be at least 8 characters.', variant: 'error' });
      return;
    }
    if (password !== confirm) {
      setSignupError('Passwords do not match.');
      toast({ title: 'Password mismatch', description: 'Passwords do not match.', variant: 'error' });
      return;
    }
    setSignupLoading(true);
    try {
      const data = await fetchApi<RegisterResponse>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (data.success) {
        setRegisteredEmail(email);
        toast({
          title: 'Verify your email',
          description: 'A verification link has been sent to your email. Please verify to activate your account.',
          variant: 'success',
        });
        setShowRegistrationStatus(true);
      } else {
        setSignupError(data.error?.message || 'Sign up failed.');
        toast({ title: 'Sign up failed', description: data.error?.message || 'Sign up failed.', variant: 'error' });
      }
    } catch (error) {
      console.error('Registration error:', error);
      setSignupError('Network error. Please try again.');
      toast({ title: 'Network error', description: 'Please try again.', variant: 'error' });
    } finally {
      setSignupLoading(false);
    }
  };

  // Separate providers
  const allProviders = Object.values(providers);
  const oauthProviders = allProviders.filter((p) => p && p.id !== 'credentials');
  const credentialsProvider = allProviders.find((p) => p && p.id === 'credentials');

  return (
    <main className="flex min-h-screen bg-background">
      {/* Left: Card */}
      <section className="w-full md:w-1/2 flex flex-col justify-center items-center px-4 py-12 min-h-screen">
        <div className="w-full max-w-md rounded-2xl bg-card/95 shadow-2xl border border-border p-8 flex flex-col gap-6 relative transition-all duration-300">
          <div>
            <h1 className="text-2xl font-bold text-card-foreground mb-1">
              {mode === 'signin' ? 'Sign into your account' : 'Create your account'}
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
              {mode === 'signin'
                ? 'The secure, metadata-powered platform for AI, LLM, and data privacy workflows.'
                : 'Sign up for Encypher and unlock secure, metadata-powered AI workflows.'}
            </p>
          </div>
          {/* OAuth Providers (horizontal row) - both modes */}
          {oauthProviders.length > 0 && (
            <div className="flex flex-row gap-3 w-full mb-2">
              {oauthProviders.filter(Boolean).map((provider) =>
                provider ? (
                  <button
                    key={provider.id}
                    className={`flex items-center justify-center gap-2 flex-1 py-3 px-2 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring
                      bg-background text-foreground border border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm group`}
                    onClick={() => signIn(provider.id, { callbackUrl: process.env.NEXT_PUBLIC_DASHBOARD_URL || "https://dashboard.encypherai.com" })}
                    aria-label={`Sign in with ${provider.name}`}
                    style={{ boxShadow: provider.id === 'google' ? '0 2px 10px 0 #4285F4' : provider.id === 'github' ? '0 2px 10px 0 #4285F4' : provider.id === 'discord' ? '0 2px 10px 0 #5865F2' : '0 2px 10px 0 var(--blue-ncs, #2a87c4)' }}
                  >
                    {provider.id === 'google' && <GoogleIcon />}
                    {provider.id === 'github' && <GitHubIcon />}
                    {provider.id === 'discord' && <DiscordIcon />}
                    <span className="text-base font-medium">{provider.name}</span>
                  </button>
                ) : null
              )}
            </div>
          )}
          {/* Separator */}
          <div className="flex items-center gap-2 my-2">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">
              {mode === 'signin' ? 'or sign in with' : 'or sign up with'}
            </span>
            <div className="flex-1 h-px bg-border" />
          </div>
          {/* Credentials Form */}
          {mode === 'signin' && credentialsProvider && !showEmailNotVerified && (
            <SignInForm
              onSignIn={async (email: string, password: string) => {
                setEmail(email);
                setPassword(password);
                await handleCredentialsSignIn({ preventDefault: () => {} } as React.FormEvent<HTMLFormElement>);
              }}
              loading={loading}
              error={error}
              email={email}
              setEmail={setEmail}
              password={password}
              setPassword={setPassword}
            />
          )}
          {/* Email Not Verified State */}
          {mode === 'signin' && showEmailNotVerified && (
            <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg p-4 space-y-4">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <h3 className="font-semibold text-amber-800 dark:text-amber-200">Email Not Verified</h3>
                  <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                    Please check your inbox for the verification email we sent to <strong>{unverifiedEmail}</strong>.
                  </p>
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <button
                  type="button"
                  onClick={handleResendVerification}
                  disabled={resendLoading}
                  className="w-full py-2 px-4 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-lg transition disabled:opacity-50"
                >
                  {resendLoading ? 'Sending...' : 'Resend Verification Email'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowEmailNotVerified(false);
                    setError(null);
                  }}
                  className="w-full py-2 px-4 bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition"
                >
                  Try Different Email
                </button>
              </div>
            </div>
          )}
          {mode === 'signup' && !showRegistrationStatus && (
            <SignUpForm
              onSignUp={handleSignUp}
              loading={signupLoading}
              error={signupError}
              email={signupEmail}
              setEmail={setSignupEmail}
              password={signupPassword}
              setPassword={setSignupPassword}
              confirm={signupConfirm}
              setConfirm={setSignupConfirm}
            />
          )}
          {mode === 'signup' && showRegistrationStatus && registeredEmail && (
            <div className="text-sm text-muted-foreground mt-4 text-center">
              A verification link has been sent to your email. Please verify to activate your account.
            </div>
          )}
          {/* Toggle links */}
          <div className="flex flex-col md:flex-row items-center justify-center gap-2 mt-2 text-sm">
            <div className="text-center">
              {mode === 'signin' ? (
                <>
                  <span>Don&apos;t have an account? </span>
                  <button type="button" className="font-semibold text-accent hover:underline" onClick={() => setMode('signup')}>Sign up</button>
                  <br />
                  <button type="button" className="font-semibold text-accent hover:underline">Forgot your password?</button>
                </>
              ) : (
                <>
                  <span>Already have an account? </span>
                  <button type="button" className="font-semibold text-accent hover:underline" onClick={() => setMode('signin')}>Sign in</button>
                </>
              )}
            </div>
          </div>
          {/* Legal text */}
          <div className="text-xs text-muted-foreground mt-4 text-center">
            By using Encypher you agree to our <a href="/terms" className="underline">Terms of Service</a>, <a href="/privacy" className="underline">Privacy</a>, and Security policies and practices.
          </div>
        </div>
      </section>
      {/* Right: Animation (social proof commented out) */}
      <section className="hidden md:flex w-1/2 items-center justify-center bg-background relative overflow-hidden min-h-screen">
        <div className="absolute inset-0 w-full h-full">
          <div className="absolute inset-0 bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue opacity-80 z-0" />
          <div className="relative z-10 w-full h-full flex items-center justify-center">
            <div className="w-full h-[80vh]">
              <MetadataBackground />
            </div>
          </div>
        </div>
        {/*
        <div className="absolute bottom-24 right-16 max-w-sm w-full bg-card/90 rounded-xl shadow-lg border border-border p-5 flex items-center gap-4 z-20">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-ncs to-delft-blue flex items-center justify-center text-white font-bold text-2xl">E</div>
          <div>
            <div className="font-semibold text-card-foreground">@trusted_user</div>
            <div className="text-sm text-muted-foreground">“Encypher made our workflow seamless and secure. Highly recommend!”</div>
          </div>
        </div>
        */}
      </section>
    </main>
  );
}

// Define the API response type
interface RegisterResponse {
  success: boolean;
  data?: {
    message: string;
  };
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

// Wrap the component with Suspense to handle useRouter
export default function SignInPage(props: SignInPageProps) {
  return (
    <Suspense fallback={<SignInLoading />}>
      <SignInContent {...props} />
    </Suspense>
  );
}
