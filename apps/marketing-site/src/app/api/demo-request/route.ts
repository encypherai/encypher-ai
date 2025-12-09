import { NextRequest, NextResponse } from 'next/server';

/**
 * API route to handle demo requests from the marketing site.
 * 
 * Architecture:
 * - Development: Logs the request and returns success (no backend required)
 * - Production: Forwards to the notification-service via API Gateway
 * 
 * The notification-service (port 8008) handles:
 * - Storing demo requests in the database
 * - Sending confirmation emails to users
 * - Sending notification emails to sales team
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Log the demo request (useful for both dev and prod debugging)
    console.log('[Demo Request]', {
      name: body.name,
      email: body.email,
      organization: body.organization,
      role: body.role,
      source: body.source,
      context: body.context,
      timestamp: new Date().toISOString(),
    });

    // In production, forward to notification-service via API Gateway
    const gatewayUrl = process.env.GATEWAY_URL || process.env.NEXT_PUBLIC_GATEWAY_URL;
    const isProduction = process.env.NODE_ENV === 'production';
    
    if (gatewayUrl && isProduction) {
      // Route based on context
      const endpoint = body.context === 'ai' 
        ? '/api/v1/notifications/demo-requests/ai'
        : body.context === 'enterprise'
        ? '/api/v1/notifications/demo-requests/enterprise'
        : '/api/v1/notifications/demo-requests/publisher';
      
      const response = await fetch(`${gatewayUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
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
