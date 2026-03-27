/**
 * Encypher CDN Provenance — Lambda@Edge viewer-response handler
 *
 * Trigger type: viewer-response (CloudFront)
 *
 * CloudFront function configuration:
 *   - Event: viewer response
 *   - Origin: your image origin
 *
 * Environment variables (set on Lambda function):
 *   ENCYPHER_API_URL  — e.g. "https://api.encypher.com"
 *
 * Note: Lambda@Edge functions run in us-east-1 and are replicated to edge
 * locations. They cannot use environment variables directly in the handler —
 * the API URL must be hardcoded or fetched from SSM Parameter Store at init.
 * For simplicity this implementation uses a module-level constant that the
 * deployer replaces via the provided deployment script or CDK/Terraform.
 */

// REPLACE with your Encypher API base URL before deploying
const ENCYPHER_API_URL = process.env.ENCYPHER_API_URL || 'https://api.encypher.com';

// In-process cache: Map<canonicalUrl, {manifestUrl, expiresAt}>
const manifestCache = new Map();
const CACHE_TTL_MS = 3_600_000; // 1 hour

const IMAGE_CONTENT_TYPES = new Set([
  'image/jpeg', 'image/jpg', 'image/png', 'image/webp',
  'image/gif', 'image/avif', 'image/tiff',
]);

const RESIZE_PARAMS = new Set(['width', 'height', 'format', 'quality', 'w', 'h', 'q', 'fit', 'auto']);

/**
 * Strip CloudFront/CDN transform parameters to recover canonical URL.
 * CloudFront typically uses query params for image optimization.
 */
function getCanonicalUrl(cf) {
  const { uri, querystring, domainName } = cf.request || {};

  // Build base URL
  const qs = querystring || '';
  const params = new URLSearchParams(qs);
  for (const key of [...params.keys()]) {
    if (RESIZE_PARAMS.has(key)) params.delete(key);
  }

  const cleanQs = params.toString();
  const cleanUri = uri || '/';
  const base = `https://${domainName || 'unknown'}${cleanUri}`;
  return cleanQs ? `${base}?${cleanQs}` : base;
}

/**
 * Look up manifest URL from Encypher API, with in-process caching.
 */
async function lookupManifestUrl(canonicalUrl) {
  const cached = manifestCache.get(canonicalUrl);
  if (cached && Date.now() < cached.expiresAt) {
    return cached.manifestUrl; // may be null (negative cache)
  }

  const apiUrl = `${ENCYPHER_API_URL}/api/v1/cdn/manifests/lookup?url=${encodeURIComponent(canonicalUrl)}`;

  try {
    const resp = await fetch(apiUrl, {
      headers: { Accept: 'application/json', 'User-Agent': 'Encypher-Lambda-Edge/1.0' },
      signal: AbortSignal.timeout(3000), // 3s timeout
    });

    if (resp.ok) {
      const data = await resp.json();
      const manifestUrl = `${ENCYPHER_API_URL}/api/v1/cdn/manifests/${data.record_id}`;
      manifestCache.set(canonicalUrl, { manifestUrl, expiresAt: Date.now() + CACHE_TTL_MS });
      return manifestUrl;
    }

    if (resp.status === 404) {
      // Negative cache (shorter TTL)
      manifestCache.set(canonicalUrl, { manifestUrl: null, expiresAt: Date.now() + 300_000 });
    }
  } catch {
    // API unavailable — fail open
  }

  return null;
}

/**
 * Lambda@Edge viewer-response handler entry point.
 *
 * @param {Object} event - CloudFront viewer-response event
 * @returns {Object} Modified CloudFront response
 */
export const handler = async (event) => {
  const { cf } = event.Records[0];
  const response = cf.response;

  // Only process image responses
  const contentTypeHeader = response.headers['content-type']?.[0]?.value || '';
  const mimeBase = contentTypeHeader.split(';')[0].trim().toLowerCase();

  if (!IMAGE_CONTENT_TYPES.has(mimeBase)) {
    return response;
  }

  // Get canonical URL
  const canonicalUrl = getCanonicalUrl(cf);

  // Look up manifest (with in-process cache)
  const manifestUrl = await lookupManifestUrl(canonicalUrl);

  if (manifestUrl) {
    response.headers['c2pa-manifest-url'] = [{ key: 'C2PA-Manifest-URL', value: manifestUrl }];
    response.headers['x-encypher-provenance'] = [{ key: 'X-Encypher-Provenance', value: 'active' }];
  }

  return response;
};
