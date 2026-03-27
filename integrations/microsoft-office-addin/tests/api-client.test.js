const test = require('node:test');
const assert = require('node:assert/strict');

const { ensureHttpsEncypherHost, signContent } = require('../src/api-client');

test('ensureHttpsEncypherHost allows https encypherai domains', () => {
  assert.equal(ensureHttpsEncypherHost('https://api.encypher.com'), 'https://api.encypher.com');
  assert.equal(ensureHttpsEncypherHost('https://staging.encypher.com/v1'), 'https://staging.encypher.com');
});

test('ensureHttpsEncypherHost rejects non-https URLs', () => {
  assert.throws(() => ensureHttpsEncypherHost('http://api.encypher.com'));
});

test('ensureHttpsEncypherHost rejects non-encypher domains', () => {
  assert.throws(() => ensureHttpsEncypherHost('https://example.com'));
});

test('signContent sends sentence + micro_ecc_c2pa defaults', async () => {
  const originalFetch = global.fetch;
  let captured = null;
  const embeddingPlan = {
    index_unit: 'codepoint',
    operations: [{ insert_after_index: 0, marker: '\\uFE00' }],
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
              document_id: 'doc_1',
              verification_url: 'https://verify.encypher.com/doc_1',
            },
          },
        };
      },
    };
  };

  try {
    const result = await signContent({
      apiBaseUrl: 'https://api.encypher.com',
      apiKey: 'ency_key',
      text: 'hello',
      title: 'Office Content',
    });

    assert.ok(captured);
    const body = JSON.parse(captured.options.body);
    assert.equal(body.options.segmentation_level, 'sentence');
    assert.equal(body.options.manifest_mode, 'micro_ecc_c2pa');
    assert.equal(body.options.document_type, 'article');
    assert.equal(body.options.return_embedding_plan, true);
    assert.deepEqual(result.embeddingPlan, embeddingPlan);
  } finally {
    global.fetch = originalFetch;
  }
});
