import { NextRequest, NextResponse } from 'next/server';

import { resolveDemoRequestEndpoint } from '@/lib/demoRequestRouting';
import { verifyTurnstileToken } from '@/lib/turnstile';

/**
 * API route to handle demo requests from the marketing site.
 *
 * Architecture:
 * - Production: Validates Turnstile token, then forwards to web-service
 * - Development: Logs the request and returns success (no backend required)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Verify Turnstile token before processing
    const clientIp = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? null;
    const turnstile = await verifyTurnstileToken(body.turnstileToken, clientIp);
    if (!turnstile.success) {
      console.warn('[Demo Request] Turnstile verification failed:', turnstile.error);
      return NextResponse.json(
        { success: false, error: turnstile.error },
        { status: 403 }
      );
    }

    // Strip turnstile token before forwarding to backend
    const { turnstileToken: _removed, ...forwardBody } = body;

    // Log the demo request (useful for both dev and prod debugging)
    console.log('[Demo Request]', {
      name: forwardBody.name,
      email: forwardBody.email,
      organization: forwardBody.organization,
      role: forwardBody.role,
      source: forwardBody.source,
      context: forwardBody.context,
      timestamp: new Date().toISOString(),
    });

    const isProduction = process.env.NODE_ENV === 'production';
    const webServiceUrl = process.env.WEB_SERVICE_URL || process.env.NEXT_PUBLIC_WEB_SERVICE_URL;

    if (isProduction && !webServiceUrl) {
      console.error('[Demo Request] Missing WEB_SERVICE_URL in production');
      return NextResponse.json(
        { success: false, error: 'Server misconfiguration' },
        { status: 500 }
      );
    }

    if (webServiceUrl) {
      if (forwardBody.context && !['ai', 'publisher', 'enterprise', 'general'].includes(forwardBody.context)) {
        console.warn('[Demo Request] Unknown context, defaulting to general:', forwardBody.context);
      }
      const endpoint = resolveDemoRequestEndpoint(forwardBody.context);

      const response = await fetch(`${webServiceUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(forwardBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[Demo Request] Gateway error:', response.status, errorText);
        throw new Error(`Gateway returned ${response.status}`);
      }

      const data = await response.json();
      return NextResponse.json(data);
    }

    // In development, just return success (no backend required)
    console.log('[Demo Request] Development mode - request logged, returning success');
    return NextResponse.json({
      success: true,
      id: `dev-${Date.now()}`,
      message: 'Demo request received successfully. We\'ll contact you within 24 hours.',
    });

  } catch (error) {
    console.error('[Demo Request Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to submit demo request. Please contact sales@encypher.com'
      },
      { status: 500 }
    );
  }
}

// Handle OPTIONS for CORS preflight (shouldn't be needed for same-origin but good to have)
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
