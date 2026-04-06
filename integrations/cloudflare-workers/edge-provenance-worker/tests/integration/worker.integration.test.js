/**
 * Integration tests for the Edge Provenance Worker.
 *
 * Runs the full Worker inside Miniflare (the same workerd runtime used by
 * wrangler dev) with outbound fetch calls intercepted via fetchMock.
 * No live API or network access required.
 */

import { describe, it, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { Miniflare, createFetchMock } from 'miniflare';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MARKER_VS1 = '\uFE00';

const ARTICLE_HTML = `<!DOCTYPE html>
<html><head><title>Test Article</title></head><body>
<article>
  <p>The quick brown fox jumps over the lazy dog. This sentence contains enough text to pass the minimum character threshold for provenance signing.</p>
  <p>A second paragraph adds additional content so the article reaches the required length. Publishers need multiple paragraphs to create realistic test scenarios.</p>
</article>
</body></html>`;

const SHORT_ARTICLE_HTML = `<!DOCTYPE html>
<html><head><title>Short</title></head><body>
<article><p>Too short.</p></article>
</body></html>`;

const TINY_HTML = '<html><body>Hi</body></html>';

const PROVISION_RESPONSE = {
  success: true,
  org_id: 'org-test-123',
  domain_token: 'token-abc',
  dashboard_url: 'https://dashboard.encypher.com',
  claim_url: 'https://dashboard.encypher.com/claim',
};

const SIGN_RESPONSE = {
  success: true,
  document_id: 'doc-test-001',
  verification_url: 'https://verify.encypher.com/doc-test-001',
  embedding_plan: {
    index_unit: 'codepoint',
    operations: [{ insert_after_index: 10, marker: MARKER_VS1 }],
  },
};

// ---------------------------------------------------------------------------
// Miniflare factory
// ---------------------------------------------------------------------------

function createTestWorker(fetchMock) {
  return new Miniflare({
    modules: true,
    modulesRules: [{ type: 'ESModule', include: ['**/*.js'] }],
    scriptPath: './src/worker.js',
    kvNamespaces: ['PROVENANCE_CACHE'],
    fetchMock,
  });
}

function mockOriginHtml(fetchMock, path, html) {
  const origin = fetchMock.get('https://example.com');
  origin.intercept({ path, method: 'GET' })
    .reply(200, html, { headers: { 'content-type': 'text/html; charset=utf-8' } });
}

function mockOriginNonHtml(fetchMock, path, body, contentType) {
  const origin = fetchMock.get('https://example.com');
  origin.intercept({ path, method: 'GET' })
    .reply(200, body, { headers: { 'content-type': contentType } });
}

function mockProvisionSuccess(fetchMock) {
  const api = fetchMock.get('https://api.encypher.com');
  api.intercept({ path: '/api/v1/public/cdn/provision', method: 'POST' })
    .reply(200, JSON.stringify(PROVISION_RESPONSE), {
      headers: { 'content-type': 'application/json' },
    });
}

function mockSignSuccess(fetchMock) {
  const api = fetchMock.get('https://api.encypher.com');
  api.intercept({ path: '/api/v1/public/cdn/sign', method: 'POST' })
    .reply(200, JSON.stringify(SIGN_RESPONSE), {
      headers: { 'content-type': 'application/json' },
    });
}

function mockProvisionFailure(fetchMock) {
  const api = fetchMock.get('https://api.encypher.com');
  api.intercept({ path: '/api/v1/public/cdn/provision', method: 'POST' })
    .reply(500, JSON.stringify({ error: 'internal_error' }), {
      headers: { 'content-type': 'application/json' },
    });
}

function mockSignFailure(fetchMock) {
  const api = fetchMock.get('https://api.encypher.com');
  api.intercept({ path: '/api/v1/public/cdn/sign', method: 'POST' })
    .reply(500, JSON.stringify({ error: 'internal_error' }), {
      headers: { 'content-type': 'application/json' },
    });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Edge Provenance Worker integration', () => {
  let fetchMock;
  let mf;

  before(() => {
    fetchMock = createFetchMock();
    fetchMock.activate();
    fetchMock.disableNetConnect();
    mf = createTestWorker(fetchMock);
  });

  after(async () => {
    await mf.dispose();
  });

  // --- Successful signing ---

  it('signs an article and sets X-Encypher-Provenance: active', async () => {
    mockOriginHtml(fetchMock, '/article', ARTICLE_HTML);
    mockProvisionSuccess(fetchMock);
    mockSignSuccess(fetchMock);

    const resp = await mf.dispatchFetch('https://example.com/article');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.get('X-Encypher-Provenance'), 'active');

    const html = await resp.text();
    assert.ok(html.includes(MARKER_VS1), 'output must contain VS marker');
    assert.ok(html.includes('Encypher Provenance'), 'output must contain verification comment');
  });

  // --- Cache hit ---

  it('serves from KV cache on second request without calling API', async () => {
    // The first test already signed ARTICLE_HTML on example.com and populated
    // the KV cache. This request uses the same domain + content hash, so the
    // cached plan is used. No API mocks -- if the Worker calls the API,
    // fetchMock throws because disableNetConnect is set.
    mockOriginHtml(fetchMock, '/article-cached', ARTICLE_HTML);

    const resp = await mf.dispatchFetch('https://example.com/article-cached');
    assert.equal(resp.headers.get('X-Encypher-Provenance'), 'active');

    const html = await resp.text();
    assert.ok(html.includes(MARKER_VS1), 'cached plan must produce markers');
  });

  // --- Static asset pass-through ---

  it('passes through CSS files without processing', async () => {
    mockOriginNonHtml(fetchMock, '/styles.css', 'body{color:red}', 'text/css');

    const resp = await mf.dispatchFetch('https://example.com/styles.css');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.has('X-Encypher-Provenance'), false);
  });

  it('passes through JSON responses without processing', async () => {
    mockOriginNonHtml(fetchMock, '/api-data', '{"ok":true}', 'application/json');

    const resp = await mf.dispatchFetch('https://example.com/api-data');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.has('X-Encypher-Provenance'), false);
  });

  // --- Admin and system paths ---

  it('skips /wp-admin/ paths', async () => {
    const origin = fetchMock.get('https://example.com');
    origin.intercept({ path: '/wp-admin/edit.php', method: 'GET' })
      .reply(200, '<html><body>admin</body></html>', {
        headers: { 'content-type': 'text/html' },
      });

    const resp = await mf.dispatchFetch('https://example.com/wp-admin/edit.php');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.has('X-Encypher-Provenance'), false);
  });

  it('skips /wp-json/ API paths', async () => {
    const origin = fetchMock.get('https://example.com');
    origin.intercept({ path: '/wp-json/wp/v2/posts', method: 'GET' })
      .reply(200, '[]', { headers: { 'content-type': 'application/json' } });

    const resp = await mf.dispatchFetch('https://example.com/wp-json/wp/v2/posts');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.has('X-Encypher-Provenance'), false);
  });

  it('skips /feed/ paths', async () => {
    const origin = fetchMock.get('https://example.com');
    origin.intercept({ path: '/feed/', method: 'GET' })
      .reply(200, '<rss></rss>', { headers: { 'content-type': 'application/xml' } });

    const resp = await mf.dispatchFetch('https://example.com/feed/');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.has('X-Encypher-Provenance'), false);
  });

  // --- Short and tiny content ---

  it('skips articles with fewer than 50 visible characters', async () => {
    mockOriginHtml(fetchMock, '/short', SHORT_ARTICLE_HTML);

    const resp = await mf.dispatchFetch('https://example.com/short');

    assert.equal(resp.status, 200);
    const provenance = resp.headers.get('X-Encypher-Provenance');
    assert.ok(provenance && provenance.startsWith('skipped:'), `expected skipped header, got: ${provenance}`);

    const html = await resp.text();
    assert.ok(!html.includes(MARKER_VS1), 'short article must not contain markers');
  });

  it('returns skipped:empty for HTML under 100 bytes', async () => {
    mockOriginHtml(fetchMock, '/tiny', TINY_HTML);

    const resp = await mf.dispatchFetch('https://example.com/tiny');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.get('X-Encypher-Provenance'), 'skipped:empty');
  });

  // --- Fail-open on API errors ---

  it('serves original HTML when provision API fails', async () => {
    // Use a different domain so it doesn't hit the cached provision from prior tests
    const origin = fetchMock.get('https://prov-fail.test');
    origin.intercept({ path: '/article', method: 'GET' })
      .reply(200, ARTICLE_HTML, { headers: { 'content-type': 'text/html; charset=utf-8' } });
    mockProvisionFailure(fetchMock);

    const resp = await mf.dispatchFetch('https://prov-fail.test/article');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.get('X-Encypher-Provenance'), 'skipped:error');

    const html = await resp.text();
    assert.ok(!html.includes(MARKER_VS1), 'fail-open must not contain markers');
    assert.ok(html.includes('The quick brown fox'), 'must serve original content');
  });

  it('serves original HTML when sign API fails', async () => {
    // Use unique content so it doesn't match the KV cache from prior tests
    const uniqueHtml = ARTICLE_HTML.replace(
      'The quick brown fox',
      'Sign failure test content with different unique wording',
    );
    mockOriginHtml(fetchMock, '/sign-fail', uniqueHtml);
    mockProvisionSuccess(fetchMock);
    mockSignFailure(fetchMock);

    const resp = await mf.dispatchFetch('https://example.com/sign-fail');

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.get('X-Encypher-Provenance'), 'skipped:error');

    const html = await resp.text();
    assert.ok(!html.includes(MARKER_VS1), 'fail-open must not contain markers');
    assert.ok(html.includes('Sign failure test'), 'must serve original content');
  });

  // --- Non-GET methods ---

  it('passes through POST requests without processing', async () => {
    const origin = fetchMock.get('https://example.com');
    origin.intercept({ path: '/contact', method: 'POST' })
      .reply(200, '<html><body>Thanks</body></html>', {
        headers: { 'content-type': 'text/html' },
      });

    const resp = await mf.dispatchFetch('https://example.com/contact', {
      method: 'POST',
    });

    assert.equal(resp.status, 200);
    assert.equal(resp.headers.has('X-Encypher-Provenance'), false);
  });

  // --- Verification endpoint ---

  it('returns 404 for /.well-known/encypher-verify when not provisioned', async () => {
    // Use a different domain that has never been provisioned
    const resp = await mf.dispatchFetch('https://unprovisioned.test/.well-known/encypher-verify');

    assert.equal(resp.status, 404);
    const body = await resp.json();
    assert.equal(body.error, 'not_provisioned');
  });

  // --- Already-signed content ---

  it('skips content that already contains VS markers', async () => {
    const signedHtml = ARTICLE_HTML.replace(
      'The quick brown fox',
      `The quick${MARKER_VS1} brown fox`,
    );
    mockOriginHtml(fetchMock, '/already-signed', signedHtml);

    const resp = await mf.dispatchFetch('https://example.com/already-signed');

    assert.equal(resp.status, 200);
    const provenance = resp.headers.get('X-Encypher-Provenance');
    assert.ok(
      provenance && provenance.startsWith('skipped:'),
      `already-signed content should be skipped, got: ${provenance}`,
    );
  });
});
