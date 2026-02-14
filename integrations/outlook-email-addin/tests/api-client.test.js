const test = require('node:test');
const assert = require('node:assert/strict');

const { ensureAllowedApiUrl } = require('../src/api-client');

test('ensureAllowedApiUrl accepts https encypherai domains', () => {
  assert.equal(ensureAllowedApiUrl('https://api.encypherai.com'), 'https://api.encypherai.com');
  assert.equal(ensureAllowedApiUrl('https://staging.encypherai.com/v1'), 'https://staging.encypherai.com');
});

test('ensureAllowedApiUrl rejects non-https URLs', () => {
  assert.throws(() => ensureAllowedApiUrl('http://api.encypherai.com'));
});

test('ensureAllowedApiUrl rejects non-encypher host', () => {
  assert.throws(() => ensureAllowedApiUrl('https://example.com'));
});
