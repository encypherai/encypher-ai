import { NextRequest, NextResponse } from 'next/server';
import { verifyTurnstileToken } from '@/lib/turnstile';

const API_BASE = (
  process.env.API_BASE_INTERNAL ||
  process.env.API_BASE ||
  process.env.NEXT_PUBLIC_API_URL ||
  'https://api.encypher.com/api/v1'
).replace(/\/$/, '');

/**
 * Proxy for forgot-password that validates Turnstile before forwarding to the backend.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { turnstileToken, ...forwardData } = body;

    // Verify Turnstile token
    const clientIp = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? null;
    const turnstile = await verifyTurnstileToken(turnstileToken, clientIp);
    if (!turnstile.success) {
      console.warn('[ForgotPassword] Turnstile verification failed:', turnstile.error);
      return NextResponse.json(
        { success: false, detail: turnstile.error },
        { status: 403 }
      );
    }

    // Forward to backend
    const res = await fetch(`${API_BASE}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(forwardData),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('[ForgotPassword] Error:', err);
    return NextResponse.json(
      { success: false, detail: 'An error occurred. Please try again.' },
      { status: 500 }
    );
  }
}
