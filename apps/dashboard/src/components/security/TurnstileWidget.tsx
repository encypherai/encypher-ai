'use client';

import { Turnstile } from '@marsidev/react-turnstile';
import { useCallback, useRef } from 'react';
import type { TurnstileInstance } from '@marsidev/react-turnstile';

interface TurnstileWidgetProps {
  onVerify: (token: string) => void;
  onExpire?: () => void;
  onError?: () => void;
  action?: string;
  className?: string;
}

const SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY || '';

/**
 * Cloudflare Turnstile widget in "managed" mode.
 *
 * - Invisible for most users (Cloudflare decides risk).
 * - Shows a visual challenge only for suspicious traffic.
 * - Renders nothing if no site key is configured (dev fallback).
 */
export default function TurnstileWidget({
  onVerify,
  onExpire,
  onError,
  action,
  className,
}: TurnstileWidgetProps) {
  const ref = useRef<TurnstileInstance | null>(null);

  const handleExpire = useCallback(() => {
    ref.current?.reset();
    onExpire?.();
  }, [onExpire]);

  const handleError = useCallback(() => {
    onError?.();
  }, [onError]);

  // No site key = skip rendering (dev mode without Turnstile configured)
  if (!SITE_KEY) {
    return null;
  }

  return (
    <Turnstile
      ref={ref}
      siteKey={SITE_KEY}
      onSuccess={onVerify}
      onExpire={handleExpire}
      onError={handleError}
      options={{
        action,
        theme: 'auto',
        size: 'flexible',
      }}
      className={className}
    />
  );
}

/**
 * Reset and get a fresh token from a Turnstile ref.
 * Useful when a form submission fails and needs a new token.
 */
export function resetTurnstile(ref: React.RefObject<TurnstileInstance | null>) {
  ref.current?.reset();
}
