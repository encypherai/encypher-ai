import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Marketing site middleware
 * 
 * TEAM_006: Removed dead /pitch route protection (no longer needed)
 * 
 * Currently this middleware is a pass-through. It can be extended
 * for future needs like:
 * - A/B testing
 * - Geo-based redirects
 * - Analytics tracking
 */
export async function middleware(_request: NextRequest) {
  // Pass through all requests
  return NextResponse.next();
}

// No paths currently need middleware protection
export const config = {
  matcher: [],
};
