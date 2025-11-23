import React, { useEffect, useState } from 'react';
import { fetchApi } from '@/lib/api';

interface RegistrationStatusProps {
  email: string;
  onVerified?: () => void;
}

type Status = 'pending' | 'verified' | 'expired' | 'error';
const MAX_RESEND_ATTEMPTS = 3;
const RESEND_COOLDOWN_SEC = 30;

export const RegistrationStatus: React.FC<RegistrationStatusProps> = ({ email, onVerified }) => {
  const [status, setStatus] = useState<Status>('pending');
  const [message, setMessage] = useState<string>('');
  const [resendLoading, setResendLoading] = useState(false);
  const [resendSuccess, setResendSuccess] = useState<string | null>(null);
  const [resendError, setResendError] = useState<string | null>(null);
  const [resendAttempts, setResendAttempts] = useState(0);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    let stopped = false;
    const poll = async () => {
      try {
        const res: { success: boolean; data?: { status: Status }; error?: { message?: string } } = await fetchApi(`/api/v1/auth/registration-status?email=${encodeURIComponent(email)}`);
        if (res && typeof res === 'object' && 'success' in res && 'data' in res) {
          setStatus(res.data?.status as Status);
          if (res.data?.status === 'verified') {
            setMessage('Email verified! You may now sign in.');
            if (onVerified) onVerified();
            stopped = true;
          } else if (res.data?.status === 'pending') {
            setMessage('Check your inbox for a verification link…');
          } else if (res.data?.status === 'expired') {
            setMessage('Verification link expired. Please register again.');
            stopped = true;
          }
        } else {
          setStatus('error');
          setMessage(res?.error?.message || 'An error occurred.');
          stopped = true;
        }
      } catch {
        setStatus('error');
        setMessage('Network error. Please try again.');
        stopped = true;
      }
    };
    poll();
    const interval = setInterval(() => {
      if (!stopped) poll();
    }, 4000);
    return () => clearInterval(interval);
  }, [email, onVerified]);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleResend = async () => {
    setResendLoading(true);
    setResendSuccess(null);
    setResendError(null);
    try {
      const res: { success: boolean; error?: { message?: string }; data?: { message?: string } } = await fetchApi('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      if (res.success) {
        setResendSuccess('Verification email resent! Check your inbox.');
        setResendAttempts(a => a + 1);
        setCooldown(RESEND_COOLDOWN_SEC);
      } else {
        setResendError(res?.error?.message || 'Failed to resend verification email.');
      }
    } catch {
      setResendError('Network error. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const resendDisabled = resendLoading || cooldown > 0 || resendAttempts >= MAX_RESEND_ATTEMPTS;

  return (
    <div className="w-full max-w-md rounded-2xl bg-card/95 shadow-2xl border border-border p-8 flex flex-col gap-6 relative transition-all duration-300 items-center mt-4" aria-live="polite" aria-label="Registration status">
      <h1 className="text-2xl font-bold text-card-foreground mb-1">{status === 'verified' ? 'Email verified!' : status === 'expired' ? 'Verification Expired' : status === 'error' ? 'Error' : 'Check your email'}</h1>
      <div className={`text-base font-medium text-center ${status === 'verified' ? 'text-green-600' : status === 'expired' || status === 'error' ? 'text-red-600' : 'text-blue-700'}`}>{message}</div>
      {status === 'pending' && (
        <>
          <button className="text-primary underline text-sm mt-2" onClick={handleResend} disabled={resendDisabled} aria-busy={resendLoading} aria-label="Resend verification email">
            {resendLoading ? 'Resending...' : cooldown > 0 ? `Resend available in ${cooldown}s` : 'Resend verification email'}
          </button>
          {resendSuccess && <div className="text-green-600 text-sm" role="status">{resendSuccess}</div>}
          {resendError && <div className="text-red-600 text-sm" role="alert">{resendError}</div>}
          <button className="underline text-sm text-blue-700 hover:text-blue-900 mt-2" onClick={onVerified} type="button" aria-label="Already verified? Sign in">Already verified? Sign in</button>
        </>
      )}
      {status === 'verified' && (
        <button className="mt-4 px-4 py-2 rounded bg-primary text-primary-foreground font-semibold shadow" onClick={onVerified} aria-label="Go to Sign In">Go to Sign In</button>
      )}
    </div>
  );
};
