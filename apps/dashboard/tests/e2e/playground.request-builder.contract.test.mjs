import assert from 'node:assert';
import { describe, it } from 'node:test';

import {
  buildRequestBodyJson,
  buildRequestObject,
  parseRequestBodyJson,
} from '../../src/lib/playgroundRequestBuilder.mjs';

describe('Playground request builder (contract)', () => {
  it('builds verify body and requires text', () => {
    assert.deepEqual(buildRequestObject('verify', { text: 'hello' }), { text: 'hello' });
    assert.throws(() => buildRequestObject('verify', { text: '   ' }), /verify\.text is required/);
  });

  it('builds lookup body and requires sentence_text', () => {
    assert.deepEqual(buildRequestObject('lookup', { sentence_text: 'hello world' }), {
      sentence_text: 'hello world',
    });
    assert.throws(
      () => buildRequestObject('lookup', { sentence_text: '' }),
      /lookup\.sentence_text is required/
    );
  });

  it('builds sign body (minimal and with optional fields)', () => {
    assert.deepEqual(buildRequestObject('sign', { text: 'hi' }), { text: 'hi' });

    assert.deepEqual(
      buildRequestObject('sign', {
        text: 'hi',
        document_title: 'Title',
        document_type: 'article',
        template_id: 'tmpl_123',
      }),
      {
        document_title: 'Title',
        document_type: 'article',
        text: 'hi',
        template_id: 'tmpl_123',
      }
    );

    assert.throws(() => buildRequestObject('sign', { text: '' }), /sign\.text is required/);
  });

  it('buildRequestBodyJson emits stable pretty JSON', () => {
    const json = buildRequestBodyJson('verify', { text: 'hello' });
    assert.equal(json, '{\n  "text": "hello"\n}');
  });

  it('parseRequestBodyJson returns best-effort values and null for invalid JSON', () => {
    assert.equal(parseRequestBodyJson('verify', '{'), null);
    assert.deepEqual(parseRequestBodyJson('verify', '{"text":"abc"}'), { text: 'abc' });
    assert.deepEqual(parseRequestBodyJson('lookup', '{"sentence_text":"abc"}'), { sentence_text: 'abc' });
    assert.deepEqual(parseRequestBodyJson('sign', '{"text":"abc"}'), {
      text: 'abc',
      document_title: '',
      document_type: '',
      template_id: '',
    });
  });
});
