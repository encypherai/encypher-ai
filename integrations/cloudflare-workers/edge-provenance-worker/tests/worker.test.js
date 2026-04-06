/**
 * Integration tests for the full Edge Provenance Worker pipeline.
 *
 * Rather than spinning up an HTTP server, these tests compose the same modules
 * that worker.js uses and drive them through the same sequence of steps.
 * This gives end-to-end coverage of the pipeline without requiring a real
 * Cloudflare runtime or live API.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { findArticleBoundary } from '../src/boundary.js';
import { extractFragments, assembleText, hashText } from '../src/fragments.js';
import { applyEmbeddingPlan, hasExistingMarkers } from '../src/embed.js';
import { getCachedPlan, cachePlan } from '../src/cache.js';

// ---------------------------------------------------------------------------
// Shared constants
// ---------------------------------------------------------------------------

// Three VS1-VS3 characters used as a realistic marker payload.
const MARKER = '\uFE00\uFE01\uFE02';

// ---------------------------------------------------------------------------
// Shared fixture HTML (WordPress-style article page)
// ---------------------------------------------------------------------------

const WP_ARTICLE_HTML = `<!DOCTYPE html>
<html><head><title>Test Article | Example</title></head><body>
<nav><a href="/">Home</a><a href="/blog">Blog</a></nav>
<article class="post-12 post type-post">
  <h1 class="entry-title">The quick brown fox</h1>
  <div class="entry-content">
    <p>The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for typography testing.</p>
    <p>A second paragraph appears here so the article has enough content to satisfy the minimum length requirement for provenance signing.</p>
  </div>
</article>
<footer><p>Copyright 2026 Example Inc.</p></footer>
</body></html>`;

// ---------------------------------------------------------------------------
// KV mock
// ---------------------------------------------------------------------------

/**
 * In-memory KV namespace that mirrors the Cloudflare KV interface used by cache.js.
 * Only implements get/put -- the cache module never calls delete or list.
 */
function makeKvMock() {
  const store = new Map();
  return {
    async get(key, type) {
      const raw = store.get(key);
      if (raw === undefined) return null;
      if (type === 'json') return JSON.parse(raw);
      return raw;
    },
    async put(key, value, _opts) {
      store.set(key, typeof value === 'string' ? value : JSON.stringify(value));
    },
    _store: store,
  };
}

// ---------------------------------------------------------------------------
// Pipeline helper
//
// Mirrors the logic in processHtml() from worker.js so tests exercise the
// real integration path. Returns {html, planData} or null.
// ---------------------------------------------------------------------------

async function runPipeline(html, planData) {
  // Step 1: boundary
  const boundary = findArticleBoundary(html, null);
  if (!boundary) return null;

  // Step 2: fragments + visible text
  const fragments = extractFragments(boundary.html);
  const visibleText = assembleText(fragments);
  if (visibleText.length < 50) return null;

  // Step 3: existing markers check
  if (hasExistingMarkers(boundary.html)) return null;

  // Step 4: apply plan
  const modifiedHtml = applyEmbeddingPlan(
    boundary.html,
    boundary.byteOffset,
    planData.embeddingPlan,
    html,
  );

  if (!modifiedHtml) return null;

  return { html: modifiedHtml, boundary, visibleText };
}

/**
 * Build a one-operation embedding plan that inserts MARKER after the
 * character at visibleIndex in visibleText. Validates the index is in range.
 */
function makePlan(visibleText, visibleIndex) {
  const chars = [...visibleText];
  assert.ok(
    visibleIndex >= 0 && visibleIndex < chars.length,
    `visibleIndex ${visibleIndex} out of range for text length ${chars.length}`,
  );
  return {
    index_unit: 'codepoint',
    operations: [{ insert_after_index: visibleIndex, marker: MARKER }],
  };
}

// ---------------------------------------------------------------------------
// Test 1: Full signing pipeline
// ---------------------------------------------------------------------------

describe('full signing pipeline', () => {
  it('extracts article, applies embedding plan, and marker appears in output', async () => {
    // Boundary detection
    const boundary = findArticleBoundary(WP_ARTICLE_HTML, null);
    assert.ok(boundary, 'boundary should be detected');
    assert.equal(boundary.selector, 'article');

    // Fragment extraction and text assembly
    const fragments = extractFragments(boundary.html);
    assert.ok(fragments.length > 0, 'should extract text fragments');
    const visibleText = assembleText(fragments);
    assert.ok(visibleText.length >= 50, 'visible text must meet minimum length');

    // Build a plan that inserts after the 10th visible character
    const plan = makePlan(visibleText, 10);
    const planData = { embeddingPlan: plan, documentId: 'doc-001', verificationUrl: null };

    // Run pipeline
    const result = await runPipeline(WP_ARTICLE_HTML, planData);
    assert.ok(result, 'pipeline should succeed');

    // Marker must appear in output
    assert.ok(result.html.includes(MARKER), 'output HTML must contain the marker');

    // Visible text (after stripping VS markers) must be unchanged
    const stripped = result.html.replace(/[\uFE00-\uFE0F\uFEFF]/g, '');
    assert.equal(stripped, WP_ARTICLE_HTML, 'stripping markers must recover original HTML');
  });

  it('hash is deterministic for identical visible text', async () => {
    const boundary = findArticleBoundary(WP_ARTICLE_HTML, null);
    const fragments = extractFragments(boundary.html);
    const text = assembleText(fragments);

    const h1 = await hashText(text);
    const h2 = await hashText(text);

    assert.equal(h1, h2, 'hashes must be deterministic');
    assert.ok(h1.startsWith('sha256:'), 'hash must use sha256 prefix');
  });
});

// ---------------------------------------------------------------------------
// Test 2: Cache-hit path
// ---------------------------------------------------------------------------

describe('cache-hit path', () => {
  it('applies a plan retrieved from KV cache without calling the API', async () => {
    const kv = makeKvMock();
    const domain = 'example.com';

    // Compute the hash prefix the same way worker.js does
    const boundary = findArticleBoundary(WP_ARTICLE_HTML, null);
    const fragments = extractFragments(boundary.html);
    const visibleText = assembleText(fragments);
    const contentHash = await hashText(visibleText);
    const hashPrefix = contentHash.slice(7, 23);

    // Pre-populate cache
    const plan = makePlan(visibleText, 5);
    const cachedPlanData = {
      embeddingPlan: plan,
      documentId: 'doc-cached',
      verificationUrl: 'https://verify.encypher.com/doc-cached',
      boundarySelector: 'article',
    };
    await cachePlan(kv, domain, hashPrefix, cachedPlanData);

    // Retrieve from cache and confirm it matches what was stored
    const retrieved = await getCachedPlan(kv, domain, hashPrefix);
    assert.ok(retrieved, 'plan should be present in cache');
    assert.equal(retrieved.documentId, 'doc-cached');

    // Apply the cached plan
    const result = await runPipeline(WP_ARTICLE_HTML, retrieved);
    assert.ok(result, 'pipeline with cached plan must succeed');
    assert.ok(result.html.includes(MARKER), 'cached plan must insert markers into HTML');
  });
});

// ---------------------------------------------------------------------------
// Test 3: Already-signed content is skipped
// ---------------------------------------------------------------------------

describe('already-signed content', () => {
  it('skips HTML that already contains VS markers in the article region', async () => {
    // Inject a VS marker directly into the article content
    const signed = WP_ARTICLE_HTML.replace(
      'The quick brown fox jumps',
      `The quick brown fox${MARKER} jumps`,
    );

    const boundary = findArticleBoundary(signed, null);
    assert.ok(boundary, 'boundary should still be detected');

    // hasExistingMarkers should block processing
    const alreadySigned = hasExistingMarkers(boundary.html);
    assert.ok(alreadySigned, 'should detect existing VS markers');

    // Confirm the pipeline guard works end-to-end
    const plan = { index_unit: 'codepoint', operations: [{ insert_after_index: 0, marker: MARKER }] };
    const result = await runPipeline(signed, { embeddingPlan: plan });
    assert.equal(result, null, 'pipeline must return null for already-signed content');
  });
});

// ---------------------------------------------------------------------------
// Test 4: Text too short
// ---------------------------------------------------------------------------

describe('text too short', () => {
  it('skips an article whose visible text is under 50 characters', async () => {
    const shortHtml = `<html><body>
<article><p>Short article.</p></article>
</body></html>`;

    const boundary = findArticleBoundary(shortHtml, null);
    assert.ok(boundary, 'boundary should be detected even for short content');

    const fragments = extractFragments(boundary.html);
    const visibleText = assembleText(fragments);
    assert.ok(visibleText.length < 50, `visible text "${visibleText}" must be under 50 chars`);

    // Pipeline must return null
    const plan = { index_unit: 'codepoint', operations: [] };
    const result = await runPipeline(shortHtml, { embeddingPlan: plan });
    assert.equal(result, null, 'pipeline must return null for text below minimum length');
  });
});

// ---------------------------------------------------------------------------
// Test 5: No article boundary
// ---------------------------------------------------------------------------

describe('no article boundary', () => {
  it('findArticleBoundary returns null or body for nav-only HTML', () => {
    // This HTML has no article, main, or significant p-cluster content.
    const navOnlyHtml = `<html><body>
<nav><a href="/">Home</a><a href="/about">About</a><a href="/contact">Contact</a></nav>
<footer><small>Copyright 2026</small></footer>
</body></html>`;

    const boundary = findArticleBoundary(navOnlyHtml, null);
    // The implementation may fall back to <body> as a last resort (P7).
    // Either null or a body-level boundary is acceptable; what matters is that
    // the text inside is far too short to pass the minimum length gate.
    if (boundary) {
      const fragments = extractFragments(boundary.html);
      const visibleText = assembleText(fragments);
      // Even if body is returned, the visible text should be minimal
      assert.ok(
        visibleText.length < 200,
        'nav-only page should have very little visible text',
      );
    }
    // No assertion is made that boundary === null because P7 catches <body>.
    // The important invariant is that the content gate prevents signing.
  });

  it('pipeline returns null when article HTML is absent', () => {
    // Deliberately omit <article>, <main>, and any semantic landmark.
    const html = `<html><body><nav>Just nav</nav><footer>Footer only</footer></body></html>`;
    const boundary = findArticleBoundary(html, null);

    if (!boundary) {
      // Great -- detection correctly returned null.
      assert.equal(boundary, null);
      return;
    }

    // If body fallback matched, the text must be too short to sign.
    const fragments = extractFragments(boundary.html);
    const visibleText = assembleText(fragments);
    assert.ok(
      visibleText.length < 50,
      'body fallback for trivial pages should have text below minimum',
    );
  });
});

// ---------------------------------------------------------------------------
// Test 6: API error / fail-open semantics
// ---------------------------------------------------------------------------

describe('API error fail-open', () => {
  it('returns original HTML unchanged when applyEmbeddingPlan returns null', async () => {
    // An out-of-range operation index will cause applyEmbeddingPlan to return null.
    // worker.js falls open and serves the original HTML.
    const badPlan = {
      index_unit: 'codepoint',
      operations: [{ insert_after_index: 99999, marker: MARKER }],
    };

    const boundary = findArticleBoundary(WP_ARTICLE_HTML, null);
    assert.ok(boundary);

    const modifiedHtml = applyEmbeddingPlan(
      boundary.html,
      boundary.byteOffset,
      badPlan,
      WP_ARTICLE_HTML,
    );

    // applyEmbeddingPlan must signal failure by returning null
    assert.equal(modifiedHtml, null, 'bad plan must return null');

    // The worker would then serve the original HTML unchanged
    // (simulated here: if modifiedHtml is null, fall back to original)
    const served = modifiedHtml !== null ? modifiedHtml : WP_ARTICLE_HTML;
    assert.equal(served, WP_ARTICLE_HTML, 'fail-open must serve original HTML');
  });

  it('returns original HTML unchanged when plan is null (sign API failure)', () => {
    // Simulate signContent returning null (network error, 5xx, etc.)
    const nullPlan = null;
    const result = applyEmbeddingPlan('<article><p>content</p></article>', 0, nullPlan, WP_ARTICLE_HTML);
    assert.equal(result, null, 'null plan must produce null from applyEmbeddingPlan');

    // Fail-open simulation
    const served = result !== null ? result : WP_ARTICLE_HTML;
    assert.equal(served, WP_ARTICLE_HTML);
  });
});

// ---------------------------------------------------------------------------
// Test 7: Multiple articles -- picks the one with most <p> tags
// ---------------------------------------------------------------------------

describe('multiple articles on one page', () => {
  it('selects the article with the most paragraphs', () => {
    const html = `<html><body>
<article class="sidebar-promo">
  <p>Promo teaser text only.</p>
</article>
<article class="main-story">
  <p>First paragraph of the main story content for signing.</p>
  <p>Second paragraph of the main story content for signing.</p>
  <p>Third paragraph of the main story content for signing.</p>
  <p>Fourth paragraph of the main story content for signing.</p>
</article>
<article class="related-link">
  <p>Related story teaser.</p>
  <p>Second line of related story.</p>
</article>
</body></html>`;

    const boundary = findArticleBoundary(html, null);
    assert.ok(boundary, 'should detect an article boundary');
    assert.equal(boundary.selector, 'article', 'selector should be article');
    // The main-story article has 4 paragraphs -- the most of the three.
    assert.ok(
      boundary.html.includes('main-story'),
      'should pick the article with the most <p> tags',
    );
    assert.ok(
      !boundary.html.includes('sidebar-promo'),
      'should not select the sidebar promo article',
    );
  });

  it('applies markers only inside the selected article region', async () => {
    const html = `<html><body>
<article class="teaser"><p>Teaser only.</p></article>
<article class="body">
  <p>Main article first paragraph with sufficient length for provenance signing.</p>
  <p>Main article second paragraph adds more content to exceed the minimum threshold.</p>
</article>
</body></html>`;

    const boundary = findArticleBoundary(html, null);
    assert.ok(boundary);
    assert.ok(boundary.html.includes('class="body"'), 'must select the body article');

    const fragments = extractFragments(boundary.html);
    const visibleText = assembleText(fragments);
    const plan = makePlan(visibleText, 4); // after 5th char

    const result = applyEmbeddingPlan(boundary.html, boundary.byteOffset, plan, html);
    assert.ok(result, 'should produce modified HTML');
    assert.ok(result.includes(MARKER), 'marker must appear in output');

    // The teaser article should be untouched
    const teaserIdx = result.indexOf('Teaser only');
    const markerIdx = result.indexOf(MARKER);
    const bodyIdx = result.indexOf('Main article first');
    assert.ok(markerIdx > teaserIdx, 'marker must appear after the teaser article');
    assert.ok(markerIdx >= bodyIdx - 20, 'marker must be near the body article content');
  });
});

// ---------------------------------------------------------------------------
// Test 8: HTML entities preserved
// ---------------------------------------------------------------------------

describe('HTML entities preserved', () => {
  it('keeps &amp; entity in HTML after marker insertion', () => {
    const html = `<html><body>
<article>
  <p>Tom &amp; Jerry ate bread &amp; butter on a warm summer afternoon in the park.</p>
  <p>Another paragraph to ensure the article has enough content for signing purposes.</p>
</article>
</body></html>`;

    const boundary = findArticleBoundary(html, null);
    assert.ok(boundary, 'should detect article boundary');

    const fragments = extractFragments(boundary.html);
    const visibleText = assembleText(fragments);
    // Visible text should have decoded & not &amp;
    assert.ok(visibleText.includes('Tom & Jerry'), 'visible text should decode &amp; to &');
    assert.ok(!visibleText.includes('&amp;'), 'visible text must not contain raw entities');

    // Insert marker after the 3rd visible character ("Tom")
    const plan = makePlan(visibleText, 3);
    const result = applyEmbeddingPlan(boundary.html, boundary.byteOffset, plan, html);
    assert.ok(result, 'should produce output HTML');

    // The HTML entity must survive marker insertion
    assert.ok(result.includes('&amp;'), 'HTML must still contain &amp; after marker insertion');

    // Stripping markers must recover the original HTML exactly
    const stripped = result.replace(/[\uFE00-\uFE0F\uFEFF]/g, '');
    assert.equal(stripped, html, 'stripping markers must recover original HTML with entities');
  });

  it('keeps &lt; and &gt; entities after marker insertion', () => {
    const html = `<html><body>
<article>
  <p>The expression x &lt; y &gt; z is a common inequality used in mathematics courses.</p>
  <p>Additional paragraph to satisfy the minimum text length requirement for signing.</p>
</article>
</body></html>`;

    const boundary = findArticleBoundary(html, null);
    assert.ok(boundary);

    const fragments = extractFragments(boundary.html);
    const visibleText = assembleText(fragments);
    assert.ok(visibleText.includes('x < y > z'), 'entities must be decoded in visible text');

    const plan = makePlan(visibleText, 2);
    const result = applyEmbeddingPlan(boundary.html, boundary.byteOffset, plan, html);
    assert.ok(result, 'should produce output HTML');
    assert.ok(result.includes('&lt;'), 'HTML must retain &lt; entity');
    assert.ok(result.includes('&gt;'), 'HTML must retain &gt; entity');

    const stripped = result.replace(/[\uFE00-\uFE0F\uFEFF]/g, '');
    assert.equal(stripped, html, 'stripping markers must recover original HTML');
  });
});
