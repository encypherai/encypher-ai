import { NextRequest, NextResponse } from 'next/server';

/**
 * Newsletter subscription endpoint.
 *
 * Architecture mirrors demo-request:
 * - Production: Forwards to WEB_SERVICE_URL/api/v1/newsletter/subscribe
 * - Development: Logs and returns success (no backend required)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email } = body;

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
