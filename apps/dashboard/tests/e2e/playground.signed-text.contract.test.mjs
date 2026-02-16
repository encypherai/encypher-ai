import assert from 'node:assert';
import { describe, it } from 'node:test';

import { extractSignedTextFromResponse } from '../../src/lib/playgroundSignedText.mjs';

describe('Playground signed_text extraction (contract)', () => {
  it('extracts unified signed_text payload from sign response', () => {
    const signedText = 'Line 1\n\nLine 2';
    const response = JSON.stringify({
      success: true,
      data: {
        document: {
          signed_text: signedText,
        },
      },
    });

    assert.equal(extractSignedTextFromResponse(response), signedText);
  });

  it('extracts legacy signed_text payload from sign response', () => {
    const signedText = 'Legacy signed text';
    const response = JSON.stringify({
      success: true,
      signed_text: signedText,
    });

    assert.equal(extractSignedTextFromResponse(response), signedText);
  });

  it('returns null for non-sign payloads and malformed JSON', () => {
    assert.equal(extractSignedTextFromResponse('{'), null);
    assert.equal(
      extractSignedTextFromResponse(
        JSON.stringify({ success: true, data: { valid: true, reason_code: 'OK' } })
      ),
      null
    );
  });
});
