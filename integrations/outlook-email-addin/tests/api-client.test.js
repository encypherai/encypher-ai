const test = require('node:test');
const assert = require('node:assert/strict');

const { ensureAllowedApiUrl, signEmailBody } = require('../src/api-client');

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

test('signEmailBody requests embedding plan mode and returns embeddingPlan', async () => {
  const originalFetch = global.fetch;
  let captured = null;
  const embeddingPlan = {
    index_unit: 'codepoint',
    operations: [{ insert_after_index: 1, marker: '\\uFE00' }],
  };

  global.fetch = async (url, options) => {
    captured = { url, options };
    return {
      ok: true,
      async json() {
        return {
          data: {
            document: {
              signed_text: 'signed',
              embedding_plan: embeddingPlan,
            },
          },
        };
      },
    };
  };

  try {
    const result = await signEmailBody({
      apiBaseUrl: 'https://api.encypherai.com',
      apiKey: 'ency_key',
      text: 'hello',
      title: 'Outlook Email',
    });

    assert.ok(captured);
    const body = JSON.parse(captured.options.body);
    assert.equal(body.options.document_type, 'email');
    assert.equal(body.options.return_embedding_plan, true);
    assert.deepEqual(result.embeddingPlan, embeddingPlan);
  } finally {
    global.fetch = originalFetch;
  }
});
