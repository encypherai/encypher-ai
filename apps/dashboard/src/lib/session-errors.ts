/**
 * Canonical session-expiry detection.
 *
 * Merges the superset of checks previously duplicated in
 * providers.tsx and useAuthErrorHandler.ts:
 * - Response instance check (from useAuthErrorHandler)
 * - 'unauthorized' keyword (from useAuthErrorHandler)
 * - 'template' keyword (from providers)
 */
export function isSessionExpiredError(error: unknown): boolean {
  let statusCode: number | undefined;
  let errorMessage = '';

  if (error instanceof Error && 'statusCode' in error) {
    statusCode = (error as { statusCode: number }).statusCode;
    errorMessage = error.message.toLowerCase();
  } else if (typeof Response !== 'undefined' && error instanceof Response) {
    statusCode = error.status;
  }

  // 403 is always "forbidden" (permission denied), not session expiry
  if (statusCode === 403) {
    return false;
  }

  // 401 could be session expiry OR tier-gated endpoint
  if (statusCode === 401) {
    // Check for tier-related error messages (not session expiry)
    const tierRelatedMessages = [
      'tier', 'upgrade', 'plan', 'subscription', 'business', 'enterprise',
      'professional', 'feature', 'access denied', 'permission', 'template'
    ];

    if (tierRelatedMessages.some(msg => errorMessage.includes(msg))) {
      return false; // Tier-gated, not session expiry
    }

    // Check for true session expiry messages
    const sessionExpiredMessages = [
      'expired', 'invalid token', 'not authenticated', 'session',
      'jwt', 'token invalid', 'unauthorized'
    ];

    // Only treat as session expiry if message indicates it
    // OR if there's no specific message (generic 401)
    if (sessionExpiredMessages.some(msg => errorMessage.includes(msg)) || !errorMessage) {
      return true;
    }
  }

  return false;
}
