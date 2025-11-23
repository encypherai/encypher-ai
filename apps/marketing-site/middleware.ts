import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

export async function middleware(request: NextRequest) {
  // Get the pathname
  const path = request.nextUrl.pathname;

  // Check if the path is /pitch
  if (path.startsWith('/pitch')) {
    // Get the token
    const token = await getToken({
      req: request,
      secret: process.env.NEXTAUTH_SECRET,
    });

    // If there's no token, redirect to the access page
    if (!token) {
      const url = new URL('/investor-access', request.url);
      return NextResponse.redirect(url);
    }
  }

  // Continue with the request
  return NextResponse.next();
}

// Configure the middleware to run only on specific paths
export const config = {
  matcher: ['/pitch/:path*'],
};
