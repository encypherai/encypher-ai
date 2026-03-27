/**
 * Centralized environment variable helpers for robust, secure, and maintainable config.
 * Ensures all critical env vars are validated and logged.
 */

// Returns a robust, validated absolute site URL for use in metadata, SEO, and runtime logic
export function getSiteUrl(): string {
  const envUrl = typeof process !== 'undefined' ? process.env?.NEXT_PUBLIC_SITE_URL : undefined;
  if (envUrl && typeof envUrl === 'string') {
    const trimmed = envUrl.trim();
    if (trimmed.length > 0 && /^https?:\/\//.test(trimmed)) {
      try {
        // Throws if not a valid absolute URL
        new URL(trimmed);
        return trimmed;
      } catch {}
    }
  }
  if (typeof console !== 'undefined') {
    console.warn('[env] NEXT_PUBLIC_SITE_URL is missing or invalid, using default https://encypher.com');
  }
  return 'https://encypher.com';
}
