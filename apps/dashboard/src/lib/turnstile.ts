/**
 * Server-side Cloudflare Turnstile token verification.
 *
 * Call from Next.js API routes / NextAuth authorize before processing requests.
 * Returns { success: true } if valid, { success: false, error } otherwise.
 */

const TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';

interface TurnstileVerifyResult {
  success: boolean;
  error?: string;
}

export async function verifyTurnstileToken(
  token: string | undefined | null,
  remoteIp?: string | null,
): Promise<TurnstileVerifyResult> {
  const secret = process.env.TURNSTILE_SECRET_KEY;

  // In development without keys configured, skip verification
  if (!secret) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('[Turnstile] No TURNSTILE_SECRET_KEY set -- skipping verification in dev');
      return { success: true };
    }
    console.error('[Turnstile] TURNSTILE_SECRET_KEY not configured');
    return { success: false, error: 'Bot protection misconfigured' };
  }

  if (!token) {
    return { success: false, error: 'Bot verification required. Please complete the challenge.' };
  }

  try {
    const body: Record<string, string> = { secret, response: token };
    if (remoteIp) {
      body.remoteip = remoteIp;
    }

    const res = await fetch(TURNSTILE_VERIFY_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (data.success) {
      return { success: true };
    }

    console.warn('[Turnstile] Verification failed:', data['error-codes']);
    return { success: false, error: 'Bot verification failed. Please try again.' };
  } catch (err) {
    console.error('[Turnstile] Verification request error:', err);
    return { success: false, error: 'Bot verification unavailable. Please try again.' };
  }
}
