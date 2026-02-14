const test = require('node:test');
const assert = require('node:assert/strict');

const {
  isVariationSelector,
  isEmbeddingChar,
  stripEmbeddingChars,
  extractEmbeddingRuns,
  hashText,
  mergeProvenanceEntries,
} = require('../src/provenance-utils');

test('isVariationSelector returns true for VS1 and VS2 ranges', () => {
  assert.equal(isVariationSelector(0xfe00), true);
  assert.equal(isVariationSelector(0xfe0f), true);
  assert.equal(isVariationSelector(0xe0100), true);
  assert.equal(isVariationSelector(0xe01ef), true);
  assert.equal(isVariationSelector(0x41), false);
});

test('isEmbeddingChar detects VS and ZWNBSP', () => {
  assert.equal(isEmbeddingChar(0xfeff), true);
  assert.equal(isEmbeddingChar(0xfe01), true);
  assert.equal(isEmbeddingChar(0x20), false);
});

test('stripEmbeddingChars removes VS and ZWNBSP from text', () => {
  const input = 'Hel' + String.fromCodePoint(0xfeff, 0xfe00, 0xfe01) + 'lo';
  assert.equal(stripEmbeddingChars(input), 'Hello');
});

test('extractEmbeddingRuns returns contiguous embedding runs and bytes', () => {
  const input = 'A' + String.fromCodePoint(0xfeff, 0xfe00, 0xfe01) + 'B';
  const runs = extractEmbeddingRuns(input);

  assert.equal(runs.length, 1);
  assert.equal(runs[0].start, 1);
  assert.equal(runs[0].end, 4);
  assert.deepEqual(runs[0].bytes, [0, 1]);
});

test('hashText is deterministic', () => {
  assert.equal(hashText('same'), hashText('same'));
  assert.notEqual(hashText('same'), hashText('different'));
});

test('mergeProvenanceEntries appends and caps at max entries', () => {
  const existing = [{ bytes: [1], timestamp: 1 }, { bytes: [2], timestamp: 2 }];
  const additions = [{ bytes: [3] }, { bytes: [4] }];
  const merged = mergeProvenanceEntries(existing, additions, 3);

  assert.equal(merged.length, 3);
  assert.deepEqual(merged[0].bytes, [2]);
  assert.deepEqual(merged[2].bytes, [4]);
});
