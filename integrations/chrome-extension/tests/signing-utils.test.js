import { describe, it } from 'node:test';
import assert from 'node:assert';

import {
  applyEmbeddingPlanToText,
  resolveSignedText,
  withEmbeddingPlanRequest,
} from '../background/signing-utils.js';

describe('withEmbeddingPlanRequest', () => {
  it('always sets return_embedding_plan=true on outbound sign options', () => {
    const options = withEmbeddingPlanRequest({ document_type: 'article' });

    assert.strictEqual(options.document_type, 'article');
    assert.strictEqual(options.return_embedding_plan, true);
  });
});

describe('applyEmbeddingPlanToText', () => {
  it('reconstructs signed text by inserting markers at codepoint offsets', () => {
    const plan = {
      index_unit: 'codepoint',
      operations: [
        { insert_after_index: -1, marker: '\uFEFF' },
        { insert_after_index: 0, marker: '\uFE00' },
      ],
    };

    const reconstructed = applyEmbeddingPlanToText('Hi', plan);

    assert.strictEqual(reconstructed, '\uFEFFH\uFE00i');
  });

  it('returns null for invalid operations', () => {
    const plan = {
      index_unit: 'codepoint',
      operations: [{ insert_after_index: 99, marker: '\uFE00' }],
    };

    assert.strictEqual(applyEmbeddingPlanToText('Hi', plan), null);
  });
});

describe('resolveSignedText', () => {
  it('prefers signed_text when available', () => {
    const text = resolveSignedText({
      visibleText: 'Hello',
      result: { signed_text: 'signed-direct' },
    });

    assert.strictEqual(text, 'signed-direct');
  });

  it('falls back to embedding_plan reconstruction when signed_text is missing', () => {
    const text = resolveSignedText({
      visibleText: 'Hi',
      result: {
        embedding_plan: {
          index_unit: 'codepoint',
          operations: [
            { insert_after_index: 0, marker: '\uFE00' },
            { insert_after_index: 1, marker: '\uFE01' },
          ],
        },
      },
    });

    assert.strictEqual(text, 'H\uFE00i\uFE01');
  });

  it('returns null when neither signed_text nor valid embedding_plan exist', () => {
    const text = resolveSignedText({
      visibleText: 'Hello',
      result: { embedding_plan: { index_unit: 'codepoint', operations: [{ insert_after_index: 99, marker: '\uFE00' }] } },
    });

    assert.strictEqual(text, null);
  });
});
