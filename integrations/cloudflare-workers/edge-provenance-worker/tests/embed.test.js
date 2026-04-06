import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { applyEmbeddingPlan, splitChars, isVsChar, hasExistingMarkers } from '../src/embed.js';

// A VS marker character (U+FE01)
const VS_MARKER = '\uFE01';
// Multiple VS markers for a realistic plan
const MARKER_A = '\uFE00\uFE01\uFE02';
const MARKER_B = '\uFE03\uFE04\uFE05';

describe('splitChars', () => {
  it('splits ASCII string', () => {
    assert.deepEqual(splitChars('abc'), ['a', 'b', 'c']);
  });

  it('handles emoji (surrogate pairs)', () => {
    const chars = splitChars('a\u{1F600}b');
    assert.equal(chars.length, 3);
    assert.equal(chars[1], '\u{1F600}');
  });

  it('handles empty string', () => {
    assert.deepEqual(splitChars(''), []);
  });
});

describe('isVsChar', () => {
  it('detects VS1-VS16 (U+FE00-FE0F)', () => {
    assert.ok(isVsChar('\uFE00'));
    assert.ok(isVsChar('\uFE0F'));
  });

  it('detects VS17-VS256 (U+E0100-E01EF)', () => {
    assert.ok(isVsChar('\u{E0100}'));
    assert.ok(isVsChar('\u{E01EF}'));
  });

  it('detects ZWNBSP (U+FEFF)', () => {
    assert.ok(isVsChar('\uFEFF'));
  });

  it('rejects normal characters', () => {
    assert.ok(!isVsChar('A'));
    assert.ok(!isVsChar(' '));
    assert.ok(!isVsChar('\u200B')); // ZWSP is not a VS char
  });
});

describe('hasExistingMarkers', () => {
  it('returns false for clean text', () => {
    assert.ok(!hasExistingMarkers('Hello world'));
  });

  it('returns true when VS chars present', () => {
    assert.ok(hasExistingMarkers(`Hello${VS_MARKER} world`));
  });
});

describe('applyEmbeddingPlan', () => {
  it('inserts markers into simple HTML', () => {
    const html = '<p>Hello world.</p>';
    const plan = {
      index_unit: 'codepoint',
      operations: [
        { insert_after_index: 4, marker: MARKER_A }, // after 'o' in Hello
      ],
    };

    const result = applyEmbeddingPlan(
      '<p>Hello world.</p>', // boundary HTML
      0,                     // boundary offset
      plan,
      html,                  // full HTML
    );

    assert.ok(result, 'Should not return null');
    // The visible text should contain "Hello" + markers + " world."
    assert.ok(result.includes(MARKER_A), 'Should contain markers');
    // Visible text (stripped of markers) should be unchanged
    const stripped = result.replace(/[\uFE00-\uFE0F]/g, '');
    assert.equal(stripped, html);
  });

  it('handles boundary offset within larger HTML', () => {
    const fullHtml = '<nav>Menu</nav><article><p>Article text here.</p></article><footer>F</footer>';
    const boundaryHtml = '<article><p>Article text here.</p></article>';
    const boundaryOffset = fullHtml.indexOf(boundaryHtml);

    const plan = {
      index_unit: 'codepoint',
      operations: [
        { insert_after_index: 7, marker: MARKER_A }, // after "Article"
      ],
    };

    const result = applyEmbeddingPlan(boundaryHtml, boundaryOffset, plan, fullHtml);
    assert.ok(result, 'Should not return null');
    assert.ok(result.includes(MARKER_A));
    // Nav and footer should be untouched
    assert.ok(result.startsWith('<nav>Menu</nav>'));
    assert.ok(result.includes('<footer>F</footer>'));
  });

  it('handles multiple operations', () => {
    const html = '<p>First sentence. Second sentence.</p>';
    const plan = {
      index_unit: 'codepoint',
      operations: [
        { insert_after_index: 14, marker: MARKER_A }, // after first "."
        { insert_after_index: 31, marker: MARKER_B }, // after second "."
      ],
    };

    const result = applyEmbeddingPlan(html, 0, plan, html);
    assert.ok(result);
    assert.ok(result.includes(MARKER_A));
    assert.ok(result.includes(MARKER_B));
  });

  it('returns null for empty plan', () => {
    const html = '<p>Test</p>';
    const result = applyEmbeddingPlan(html, 0, { operations: [] }, html);
    // Empty operations = return original
    assert.equal(result, html);
  });

  it('returns null for null plan', () => {
    assert.equal(applyEmbeddingPlan('<p>Test</p>', 0, null, '<p>Test</p>'), null);
  });

  it('returns null for invalid index_unit', () => {
    const plan = { index_unit: 'bytes', operations: [{ insert_after_index: 0, marker: VS_MARKER }] };
    assert.equal(applyEmbeddingPlan('<p>T</p>', 0, plan, '<p>T</p>'), null);
  });

  it('returns null for out-of-range index', () => {
    const plan = {
      index_unit: 'codepoint',
      operations: [{ insert_after_index: 999, marker: VS_MARKER }],
    };
    assert.equal(applyEmbeddingPlan('<p>Short</p>', 0, plan, '<p>Short</p>'), null);
  });

  it('preserves HTML structure', () => {
    const html = '<p>Hello <em>world</em> today.</p>';
    const plan = {
      index_unit: 'codepoint',
      operations: [
        { insert_after_index: 10, marker: MARKER_A }, // after "world"
      ],
    };

    const result = applyEmbeddingPlan(html, 0, plan, html);
    assert.ok(result);
    // em tags should still be present
    assert.ok(result.includes('<em>'));
    assert.ok(result.includes('</em>'));
  });

  it('handles HTML entities correctly', () => {
    const html = '<p>Tom &amp; Jerry</p>';
    const plan = {
      index_unit: 'codepoint',
      operations: [
        { insert_after_index: 3, marker: MARKER_A }, // after "Tom"
      ],
    };

    const result = applyEmbeddingPlan(html, 0, plan, html);
    assert.ok(result);
    assert.ok(result.includes(MARKER_A));
    // Entity should be preserved
    assert.ok(result.includes('&amp;'));
  });
});
