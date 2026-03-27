import { NextRequest, NextResponse } from 'next/server';
import { verifyTurnstileToken } from '@/lib/turnstile';

/**
 * Newsletter subscription endpoint.
 *
 * Architecture mirrors demo-request:
 * - Production: Validates Turnstile token, then forwards to WEB_SERVICE_URL
 * - Development: Logs and returns success (no backend required)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, turnstileToken } = body;

    // Verify Turnstile token before processing
    const clientIp = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? null;
    const turnstile = await verifyTurnstileToken(turnstileToken, clientIp);
    if (!turnstile.success) {
      console.warn('[Newsletter Subscribe] Turnstile verification failed:', turnstile.error);
      return NextResponse.json(
        { success: false, error: turnstile.error },
        { status: 403 }
      );
    }

    if (!email || typeof email !== 'string' || !email.includes('@')) {
      return NextResponse.json(
        { success: false, error: 'A valid email address is required.' },
        { status: 400 }
      );
    }

    console.log('[Newsletter Subscribe]', {
      email,
      source: body.source || 'blog',
      timestamp: new Date().toISOString(),
    });

    const webServiceUrl = process.env.WEB_SERVICE_URL || process.env.NEXT_PUBLIC_WEB_SERVICE_URL;

    if (webServiceUrl) {
      const response = await fetch(`${webServiceUrl}/api/v1/newsletter/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: body.source || 'blog' }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[Newsletter Subscribe] Gateway error:', response.status, errorText);
        throw new Error(`Gateway returned ${response.status}`);
      }

      const data = await response.json();
      return NextResponse.json(data);
    }

    // Development: log and return success
    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('[Newsletter Subscribe Error]', error);
    return NextResponse.json(
      { success: false, error: 'Something went wrong. Please try again.' },
      { status: 500 }
    );
  }
}
