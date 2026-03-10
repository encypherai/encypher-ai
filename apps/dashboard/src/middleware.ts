import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

function buildSignInRedirect(req: NextRequest, reason?: string) {
  const { pathname, search } = req.nextUrl;
  const signInUrl = new URL('/login', req.url);
  signInUrl.searchParams.set('callbackUrl', pathname + search);
  if (reason) {
    signInUrl.searchParams.set('reason', reason);
  }
  return NextResponse.redirect(signInUrl);
}

// Enforce authentication on all routes except public ones
export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Allow public paths, health checks, static assets, and Next.js internals
  if (
    pathname.startsWith('/api/auth') ||
    pathname.startsWith('/login') ||
    pathname.startsWith('/signup') ||
    pathname.startsWith('/forgot-password') ||
    pathname.startsWith('/reset-password') ||
    pathname.startsWith('/auth/verify-email') ||
    pathname.startsWith('/wordpress/connect') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/assets') ||
    pathname === '/health' ||
    pathname === '/api/health' ||
    pathname === '/favicon.ico' ||
    pathname === '/robots.txt' ||
    pathname === '/sitemap.xml'
  ) {
    const res = NextResponse.next();
    res.headers.set('x-middleware', 'dashboard-allow');
    return res;
  }

  // Ensure we only read the dashboard's session cookie during local dev
  const cookieName = process.env.NODE_ENV === 'production'
    ? '__Secure-next-auth.session-token'
    : 'next-auth.session-token';

  const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET, cookieName });
  if (!token) {
    return buildSignInRedirect(req);
  }

  if (token.error === 'RefreshAccessTokenError') {
    return buildSignInRedirect(req, 'session_expired');
  }

  if (
    typeof token.accessTokenExpires === 'number' &&
    Date.now() >= token.accessTokenExpires &&
    !token.refreshToken
  ) {
    return buildSignInRedirect(req, 'session_expired');
  }

  const res = NextResponse.next();
  res.headers.set('x-middleware', 'dashboard-auth-ok');
  return res;
}

export const config = {
  matcher: ['/:path*'],
};
