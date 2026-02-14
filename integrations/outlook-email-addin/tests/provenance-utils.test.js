const test = require('node:test');
const assert = require('node:assert/strict');

const {
  isVariationSelector,
  isZeroWidthBase4Char,
  stripEmbeddingChars,
  extractVariationSelectorRuns,
  extractZeroWidthRuns,
  hashText,
} = require('../src/provenance-utils');

test('isVariationSelector detects VS ranges', () => {
  assert.equal(isVariationSelector(0xfe00), true);
  assert.equal(isVariationSelector(0xe0100), true);
  assert.equal(isVariationSelector(0x41), false);
});

test('isZeroWidthBase4Char detects Word-safe zero-width set', () => {
  assert.equal(isZeroWidthBase4Char(0x200c), true);
  assert.equal(isZeroWidthBase4Char(0x200d), true);
  assert.equal(isZeroWidthBase4Char(0x034f), true);
  assert.equal(isZeroWidthBase4Char(0x180e), true);
  assert.equal(isZeroWidthBase4Char(0x200b), false);
});

test('stripEmbeddingChars removes VS and zero-width chars', () => {
  const text = 'He' + String.fromCodePoint(0xfe00) + '\u200c' + 'llo';
  assert.equal(stripEmbeddingChars(text), 'Hello');
});

test('extractVariationSelectorRuns detects VS runs', () => {
  const text = 'A' + String.fromCodePoint(0xfe00, 0xfe01) + 'B';
  const runs = extractVariationSelectorRuns(text);
  assert.equal(runs.length, 1);
  assert.deepEqual(runs[0].bytes, [0, 1]);
});

test('extractZeroWidthRuns detects zero-width runs', () => {
  const text = 'A\u200c\u200d\u034f\u180eB';
  const runs = extractZeroWidthRuns(text);
  assert.equal(runs.length, 1);
  assert.equal(runs[0].length, 4);
});

test('hashText deterministic', () => {
  assert.equal(hashText('abc'), hashText('abc'));
  assert.notEqual(hashText('abc'), hashText('abd'));
});
