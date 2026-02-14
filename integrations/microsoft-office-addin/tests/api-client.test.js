const test = require('node:test');
const assert = require('node:assert/strict');

const { ensureHttpsEncypherHost } = require('../src/api-client');

test('ensureHttpsEncypherHost allows https encypherai domains', () => {
  assert.equal(ensureHttpsEncypherHost('https://api.encypherai.com'), 'https://api.encypherai.com');
  assert.equal(ensureHttpsEncypherHost('https://staging.encypherai.com/v1'), 'https://staging.encypherai.com');
});

test('ensureHttpsEncypherHost rejects non-https URLs', () => {
  assert.throws(() => ensureHttpsEncypherHost('http://api.encypherai.com'));
});

test('ensureHttpsEncypherHost rejects non-encypher domains', () => {
  assert.throws(() => ensureHttpsEncypherHost('https://example.com'));
});
