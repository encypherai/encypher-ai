/**
 * API client module for the Encypher CDN signing endpoints.
 *
 * Handles provisioning and signing calls with fail-open semantics:
 * if the API is unreachable, the worker serves unmodified HTML.
 */

const API_BASE = 'https://api.encypher.com';

/**
 * Provision a domain (or resolve existing org).
 *
 * @param {string} domain
 * @param {string|null} apiKey - If set, uses authenticated endpoints
 * @returns {Promise<Object|null>} Provisioning result or null on failure
 */
export async function provisionDomain(domain, apiKey) {
  const url = `${API_BASE}/api/v1/public/cdn/provision`;

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}),
      },
      body: JSON.stringify({
        domain,
        worker_version: '1.0.0',
      }),
    });

    if (!resp.ok) {
      console.error(`Provision failed: ${resp.status} ${resp.statusText}`);
      return null;
    }

    return await resp.json();
  } catch (err) {
    console.error('Provision request failed:', err.message);
    return null;
  }
}

/**
 * Sign article content and get an embedding plan.
 *
 * @param {string} text - Extracted article text
 * @param {string} pageUrl - Page URL
 * @param {string} orgId - Organization ID
 * @param {string|null} documentTitle
 * @param {string|null} boundarySelector - Which detection method matched
 * @param {string|null} apiKey
 * @returns {Promise<Object|null>} Sign result or null on failure
 */
export async function signContent(text, pageUrl, orgId, documentTitle, boundarySelector, apiKey) {
  const url = `${API_BASE}/api/v1/public/cdn/sign`;

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}),
      },
      body: JSON.stringify({
        text,
        page_url: pageUrl,
        org_id: orgId,
        document_title: documentTitle,
        boundary_selector: boundarySelector,
      }),
    });

    if (!resp.ok) {
      console.error(`Sign failed: ${resp.status} ${resp.statusText}`);
      return null;
    }

    return await resp.json();
  } catch (err) {
    console.error('Sign request failed:', err.message);
    return null;
  }
}
