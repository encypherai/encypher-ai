/**
 * Encypher Edge Provenance Worker
 *
 * Embeds copy-paste-survivable provenance markers into HTML article text
 * at the CDN edge. Publishers deploy with zero configuration and get
 * sentence-level micro+ECC+C2PA markers on every article.
 *
 * Environment bindings:
 *   PROVENANCE_CACHE   - KV namespace for embedding plan and provisioning cache
 *   ARTICLE_SELECTOR   - (optional) CSS selector override for article detection
 *   MIN_TEXT_LENGTH     - (optional) minimum text chars to sign (default: 50)
 *   MAX_TEXT_LENGTH     - (optional) maximum text chars (default: 51200)
 *   ENCYPHER_API_KEY   - (optional) API key for authenticated/enterprise endpoints
 */

import { findArticleBoundary } from './boundary.js';
import { extractFragments, assembleText, hashText } from './fragments.js';
import { applyEmbeddingPlan, hasExistingMarkers } from './embed.js';
import { provisionDomain, signContent } from './api.js';
import {
  getCachedPlan, cachePlan,
  getCachedProvision, cacheProvision,
  getNegativeCache, setNegativeCache,
} from './cache.js';

/**
 * Paths that should never be processed.
 */
const SKIP_PATH_PREFIXES = [
  '/api/', '/wp-admin/', '/wp-json/', '/feed/', '/sitemap',
  '/.well-known/',
];
const SKIP_EXTENSIONS = ['.xml', '.json', '.rss', '.atom', '.css', '.js', '.woff', '.woff2', '.png', '.jpg', '.gif', '.svg', '.ico'];

/**
 * Extract domain from request URL.
 */
function getDomain(url) {
  const u = new URL(url);
  let host = u.hostname;
  if (host.startsWith('www.')) host = host.slice(4);
  return host.toLowerCase();
}

/**
 * Extract page title from HTML.
 */
function extractTitle(html) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return match ? match[1].replace(/\s+/g, ' ').trim().slice(0, 500) : null;
}

/**
 * Check if request path should be skipped.
 */
function shouldSkipPath(pathname) {
  const lower = pathname.toLowerCase();
  for (const prefix of SKIP_PATH_PREFIXES) {
    if (lower.startsWith(prefix)) return true;
  }
  for (const ext of SKIP_EXTENSIONS) {
    if (lower.endsWith(ext)) return true;
  }
  return false;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Serve verification endpoint
    if (url.pathname === '/.well-known/encypher-verify') {
      return handleVerifyEndpoint(env, getDomain(request.url));
    }

    // Skip non-GET requests
    if (request.method !== 'GET') {
      return fetch(request);
    }

    // Skip paths that should not be processed
    if (shouldSkipPath(url.pathname)) {
      return fetch(request);
    }

    // Fetch the origin response
    const response = await fetch(request);

    // Only process text/html 200 responses
    const contentType = response.headers.get('Content-Type') || '';
    if (!contentType.includes('text/html') || response.status !== 200) {
      return response;
    }

    // Skip very large responses (>5MB)
    const contentLength = response.headers.get('Content-Length');
    if (contentLength && parseInt(contentLength, 10) > 5_000_000) {
      return addHeaders(response, 'skipped:oversized');
    }

    // Buffer the HTML body
    const html = await response.text();
    if (!html || html.length < 100) {
      return new Response(html, cloneResponseInit(response, 'skipped:empty'));
    }

    try {
      const result = await processHtml(html, request.url, env);
      if (result) {
        return new Response(result.html, cloneResponseInit(response, 'active', result.orgId));
      }
    } catch (err) {
      console.error('Provenance processing error:', err.message);
    }

    // Fail open: return original HTML
    return new Response(html, cloneResponseInit(response, 'skipped:error'));
  },
};

/**
 * Core processing pipeline.
 *
 * @param {string} html - Full page HTML
 * @param {string} pageUrl - Request URL
 * @param {Object} env - Worker environment bindings
 * @returns {Promise<{html: string, orgId: string}|null>}
 */
async function processHtml(html, pageUrl, env) {
  const kv = env.PROVENANCE_CACHE;
  const domain = getDomain(pageUrl);
  const minTextLength = parseInt(env.MIN_TEXT_LENGTH || '50', 10);
  const maxTextLength = parseInt(env.MAX_TEXT_LENGTH || '51200', 10);
  const apiKey = env.ENCYPHER_API_KEY || null;
  const articleSelector = env.ARTICLE_SELECTOR || null;

  // Step 1: Find article boundary
  const boundary = findArticleBoundary(html, articleSelector);
  if (!boundary) return null;

  // Step 2: Extract text fragments within boundary
  const fragments = extractFragments(boundary.html);
  const visibleText = assembleText(fragments);

  // Apply floor/ceiling
  if (visibleText.length < minTextLength) return null;
  const textToSign = visibleText.length > maxTextLength
    ? visibleText.slice(0, maxTextLength)
    : visibleText;

  // Check for existing markers
  if (hasExistingMarkers(boundary.html)) return null;

  // Step 3: Hash content for cache key
  const contentHash = await hashText(textToSign);
  const hashPrefix = contentHash.slice(7, 23); // first 16 hex chars after "sha256:"

  // Step 4: Check negative cache
  if (kv) {
    const neg = await getNegativeCache(kv, domain, hashPrefix);
    if (neg) return null;
  }

  // Step 5: Check plan cache
  let planData = kv ? await getCachedPlan(kv, domain, hashPrefix) : null;

  if (!planData) {
    // Step 6: Ensure provisioned
    let provision = kv ? await getCachedProvision(kv, domain) : null;
    if (!provision) {
      const provResult = await provisionDomain(domain, apiKey);
      if (!provResult || !provResult.success) return null;
      provision = {
        orgId: provResult.org_id,
        domainToken: provResult.domain_token,
        dashboardUrl: provResult.dashboard_url,
        claimUrl: provResult.claim_url,
      };
      if (kv) {
        ctx_waitUntil_noop(); // KV writes are fire-and-forget
        await cacheProvision(kv, domain, provision);
      }
    }

    // Step 7: Sign content
    const title = extractTitle(html);
    const signResult = await signContent(
      textToSign,
      pageUrl,
      provision.orgId,
      title,
      boundary.selector,
      apiKey,
    );

    if (!signResult || !signResult.success || !signResult.embedding_plan) {
      if (signResult && signResult.error === 'quota_exceeded') {
        // Don't negative-cache quota errors (temporary)
        return null;
      }
      if (kv) await setNegativeCache(kv, domain, hashPrefix, 'SIGN_FAIL');
      return null;
    }

    planData = {
      embeddingPlan: signResult.embedding_plan,
      documentId: signResult.document_id,
      verificationUrl: signResult.verification_url,
      boundarySelector: boundary.selector,
    };

    if (kv) await cachePlan(kv, domain, hashPrefix, planData);
  }

  // Step 8: Apply embedding plan to HTML
  const modifiedHtml = applyEmbeddingPlan(
    boundary.html,
    boundary.byteOffset,
    planData.embeddingPlan,
    html,
  );

  if (!modifiedHtml) {
    if (kv) await setNegativeCache(kv, domain, hashPrefix, 'ALIGN_FAIL');
    return null;
  }

  // Step 9: Inject HTML comment before </body>
  let finalHtml = modifiedHtml;
  const provision = kv ? await getCachedProvision(kv, domain) : null;
  if (planData.verificationUrl) {
    const comment = `<!-- Encypher Provenance: verified at ${planData.verificationUrl} -->`;
    finalHtml = finalHtml.replace('</body>', `${comment}\n</body>`);
  }

  return {
    html: finalHtml,
    orgId: provision ? provision.orgId : '',
  };
}

/**
 * Handle /.well-known/encypher-verify requests.
 */
async function handleVerifyEndpoint(env, domain) {
  const kv = env.PROVENANCE_CACHE;
  const provision = kv ? await getCachedProvision(kv, domain) : null;

  if (!provision) {
    return new Response(
      JSON.stringify({ error: 'not_provisioned' }),
      { status: 404, headers: { 'Content-Type': 'application/json' } },
    );
  }

  return new Response(
    JSON.stringify({
      domain_token: provision.domainToken,
      org_id: provision.orgId,
      worker_version: '1.0.0',
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-cache',
      },
    },
  );
}

/**
 * Create a new Response with provenance headers.
 */
function cloneResponseInit(response, provenanceStatus, orgId) {
  const headers = new Headers(response.headers);
  headers.set('X-Encypher-Provenance', provenanceStatus);
  if (orgId) headers.set('X-Encypher-Org', orgId);
  return {
    status: response.status,
    statusText: response.statusText,
    headers,
  };
}

/**
 * Add provenance headers to an existing response.
 */
function addHeaders(response, provenanceStatus) {
  const headers = new Headers(response.headers);
  headers.set('X-Encypher-Provenance', provenanceStatus);
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

// Placeholder for ctx.waitUntil patterns
function ctx_waitUntil_noop() {}
