import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

// Enforce authentication on all routes except public ones
export async function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;

  // Allow public paths and Next.js internals
  if (
    pathname.startsWith('/api/auth') ||
    pathname.startsWith('/api/health') ||
    pathname.startsWith('/login') ||
    pathname.startsWith('/_next') ||
    pathname === '/favicon.ico' ||
    pathname === '/robots.txt' ||
    pathname === '/sitemap.xml'
  ) {
    const res = NextResponse.next();
    res.headers.set('x-middleware', 'dashboard-allow');
    return res;
  }

  // Determine cookie name based on environment
  // Use __Secure- prefix when NEXTAUTH_COOKIE_DOMAIN is set (HTTPS environments)
  const isSecure = !!process.env.NEXTAUTH_COOKIE_DOMAIN;
  const cookieName = isSecure
    ? '__Secure-next-auth.session-token'
    : 'next-auth.session-token';

  const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET, cookieName });
  if (!token) {
    const signInUrl = new URL('/login', req.url);
    signInUrl.searchParams.set('callbackUrl', pathname + search);
    return NextResponse.redirect(signInUrl);
  }

  const res = NextResponse.next();
  res.headers.set('x-middleware', 'dashboard-auth-ok');
  return res;
}

export const config = {
  matcher: ['/:path*'],
};
