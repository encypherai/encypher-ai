import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Marketing site middleware
 *
 * TEAM_006: Removed dead /pitch route protection (no longer needed)
 * TEAM_011: Added security headers to prevent clickjacking, XSS, and other attacks
 */
export async function middleware(_request: NextRequest) {
  const response = NextResponse.next();

  // Security Headers
  // Prevent clickjacking - only allow framing from same origin
  response.headers.set('X-Frame-Options', 'SAMEORIGIN');

  // Prevent MIME type sniffing
  response.headers.set('X-Content-Type-Options', 'nosniff');

  // Enable XSS filter in browsers
  response.headers.set('X-XSS-Protection', '1; mode=block');

  // Control referrer information
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  // Permissions Policy - restrict dangerous features
  response.headers.set(
    'Permissions-Policy',
    'camera=(), microphone=(), geolocation=(), interest-cohort=()'
  );

  // Content Security Policy - prevent XSS and injection attacks
  // Note: Using report-only first to avoid breaking functionality
  const cspDirectives = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://www.google-analytics.com https://fonts.googleapis.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https: blob:",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://www.google-analytics.com https://backend.encypher.com https://*.encypher.com",
    "frame-src 'self'",
    "frame-ancestors 'self'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join('; ');

  response.headers.set('Content-Security-Policy', cspDirectives);

  // Strict Transport Security - force HTTPS
  response.headers.set(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains; preload'
  );

  return response;
}

// Apply to all routes
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)',
  ],
};
