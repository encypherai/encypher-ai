// integrations/cloudflare-workers/cdn-provenance-worker.js
/**
 * Encypher CDN Provenance Worker
 *
 * Intercepts image responses and injects C2PA-Manifest-URL headers
 * for images that have been registered with Encypher provenance tracking.
 *
 * Environment bindings required:
 *   ENCYPHER_API_URL  - string, e.g. "https://api.encypher.com"
 *   CDN_PROVENANCE_CACHE - KV namespace for manifest URL caching
 */

const IMAGE_CONTENT_TYPES = new Set([
  'image/jpeg', 'image/jpg', 'image/png', 'image/webp',
  'image/gif', 'image/avif', 'image/tiff',
]);

const CACHE_TTL_SECONDS = 3600;
const CDN_CIG_IMAGE_RE = /\/cdn-cgi\/image\/[^/]+\//;

/**
 * Strip Cloudflare image transform prefix to get canonical URL.
 * e.g. https://example.com/cdn-cgi/image/width=800,format=webp/https://example.com/img/photo.jpg
 *   → https://example.com/img/photo.jpg
 */
function getCanonicalUrl(url) {
  const u = new URL(url);
  // Pattern: /cdn-cgi/image/{opts}/{original-path-or-url}
  const match = u.pathname.match(/^\/cdn-cgi\/image\/[^/]+\/(.+)$/);
  if (match) {
    const rest = match[1];
    // rest might be a full URL or just a path
    try {
      return new URL(rest).toString();
    } catch {
      return `${u.origin}/${rest}`;
    }
  }
  // Also strip query params used by resize (?width=..., ?format=..., ?quality=...)
  // that some CDN configs add instead of path transforms
  const cleaned = new URL(url);
  for (const param of ['width', 'height', 'format', 'quality', 'w', 'h', 'q', 'fit']) {
    cleaned.searchParams.delete(param);
  }
  return cleaned.toString();
}

async function lookupManifest(canonicalUrl, env) {
  // Check KV cache first
  const cacheKey = `manifest:${canonicalUrl}`;
  const cached = await env.CDN_PROVENANCE_CACHE.get(cacheKey);
  if (cached !== null) {
    return cached === 'NOT_FOUND' ? null : cached;
  }

  // Call Encypher API
  const apiUrl = `${env.ENCYPHER_API_URL}/api/v1/cdn/manifests/lookup?url=${encodeURIComponent(canonicalUrl)}`;
  try {
    const resp = await fetch(apiUrl, {
      headers: { 'Accept': 'application/json' },
      cf: { cacheTtl: 0 }, // Don't use CF cache for API calls, use KV
    });
    if (resp.ok) {
      const data = await resp.json();
      const manifestUrl = `${env.ENCYPHER_API_URL}/api/v1/cdn/manifests/${data.record_id}`;
      // Cache the result
      await env.CDN_PROVENANCE_CACHE.put(cacheKey, manifestUrl, { expirationTtl: CACHE_TTL_SECONDS });
      return manifestUrl;
    } else if (resp.status === 404) {
      // Cache negative result (shorter TTL)
      await env.CDN_PROVENANCE_CACHE.put(cacheKey, 'NOT_FOUND', { expirationTtl: 300 });
      return null;
    }
  } catch (err) {
    // API unavailable — fail open (don't block the image)
    console.error('Encypher provenance lookup failed:', err.message);
  }
  return null;
}

export default {
  async fetch(request, env, ctx) {
    const response = await fetch(request);

    // Only process image responses
    const contentType = response.headers.get('Content-Type') || '';
    const mimeBase = contentType.split(';')[0].trim().toLowerCase();
    if (!IMAGE_CONTENT_TYPES.has(mimeBase)) {
      return response;
    }

    // Get canonical URL (strip CDN transform params)
    const canonicalUrl = getCanonicalUrl(request.url);

    // Look up manifest URL (async, cached in KV)
    const manifestUrl = await lookupManifest(canonicalUrl, env);
    if (!manifestUrl) {
      return response;
    }

    // Inject header into response
    const newHeaders = new Headers(response.headers);
    newHeaders.set('C2PA-Manifest-URL', manifestUrl);
    newHeaders.set('X-Encypher-Provenance', 'active');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  },
};
