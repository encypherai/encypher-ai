const test = require('node:test');
const assert = require('node:assert/strict');

const {
  isVariationSelector,
  isEmbeddingChar,
  stripEmbeddingChars,
  extractEmbeddingRuns,
  hashText,
  mergeProvenance,
} = require('../provenance-utils');

test('isVariationSelector detects VS1 and VS2 ranges', () => {
  assert.equal(isVariationSelector(0xfe00), true);
  assert.equal(isVariationSelector(0xfe0f), true);
  assert.equal(isVariationSelector(0xe0100), true);
  assert.equal(isVariationSelector(0xe01ef), true);
  assert.equal(isVariationSelector(0x41), false);
});

test('isEmbeddingChar includes ZWNBSP and VS', () => {
  assert.equal(isEmbeddingChar(0xfeff), true);
  assert.equal(isEmbeddingChar(0xfe00), true);
  assert.equal(isEmbeddingChar(0x41), false);
});

test('stripEmbeddingChars removes VS and ZWNBSP', () => {
  const text = 'He' + String.fromCodePoint(0xfeff, 0xfe00, 0xfe01) + 'llo';
  assert.equal(stripEmbeddingChars(text), 'Hello');
});

test('extractEmbeddingRuns finds contiguous embedding runs', () => {
  const text = 'A' + String.fromCodePoint(0xfeff, 0xfe00, 0xfe01) + 'B';
  const runs = extractEmbeddingRuns(text);

  assert.equal(runs.length, 1);
  assert.deepEqual(runs[0].bytes, [0, 1]);
  assert.equal(runs[0].start, 1);
  assert.equal(runs[0].end, 4);
});

test('hashText is stable and deterministic', () => {
  assert.equal(hashText('abc'), hashText('abc'));
  assert.notEqual(hashText('abc'), hashText('abcd'));
});

test('mergeProvenance appends and caps by max entries', () => {
  const existing = [{ bytes: [1], timestamp: 1 }];
  const runs = [
    { bytes: [2] },
    { bytes: [3] },
  ];

  const merged = mergeProvenance(existing, runs, 2);
  assert.equal(merged.length, 2);
  assert.deepEqual(merged[0].bytes, [2]);
  assert.deepEqual(merged[1].bytes, [3]);
});
