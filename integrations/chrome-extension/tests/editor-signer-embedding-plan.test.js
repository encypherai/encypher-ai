import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Editor signer embedding-plan DOM preservation', () => {
  it('defines a dedicated in-place embedding plan application function', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /function\s+applyEmbeddingPlanToSelectionInPlace\s*\(/,
      'Editor signer should define an embedding-plan in-place application function'
    );
  });

  it('validates embedding-plan operation bounds against visible text length', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /insert_after_index[^\n]*<\s*-1|idx\s*<\s*-1/,
      'Embedding-plan parser should reject indices before -1'
    );

    assert.match(
      signerCode,
      /insert_after_index[^\n]*>=\s*totalCodepoints|idx\s*>=\s*totalCodepoints/,
      'Embedding-plan parser should reject indices beyond visible codepoint length'
    );
  });

  it('applies embedding plan first and then falls back to signed_text replacement', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /if\s*\(response\.embeddingPlan\)\s*\{[\s\S]*applyEmbeddingPlanToSelectionInPlace/s,
      'Selection signing should attempt embedding-plan in-place insertion when available'
    );

    assert.match(
      signerCode,
      /if\s*\(!replaced\)\s*\{[\s\S]*replaceSelectionInPlace\(response\.signedText\)/s,
      'Selection signing should fall back to signed_text replacement if plan application fails'
    );
  });

  it('guards plan insertion by checking selected visible text alignment', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /rangeVisibleText\s*!==\s*visibleText/,
      'Plan application should only mutate DOM when selected visible text aligns with plan input'
    );
  });

  it('defines an online-editor fallback path for non-standard selection surfaces', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /function\s+applyEmbeddingPlanToOnlineEditorInPlace\s*\(/,
      'Editor signer should expose an online-editor-specific embedding-plan insertion fallback'
    );
  });

  it('attempts online-editor plan insertion for Google Docs and Office Online before signed_text fallback', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /const\s+onlinePlatform\s*=\s*detectOnlinePlatform\(\)/,
      'Selection signing should detect current online editor platform'
    );

    assert.match(
      signerCode,
      /onlinePlatform\s*===\s*'google-docs'\s*\|\|\s*onlinePlatform\s*===\s*'ms-word-online'/,
      'Selection signing should branch for Google Docs and Office Online surfaces'
    );

    assert.match(
      signerCode,
      /applyEmbeddingPlanToOnlineEditorInPlace\(response\.embeddingPlan,\s*visibleText,\s*onlinePlatform\)/,
      'Selection signing should try online-editor embedding-plan insertion before full replacement'
    );
  });

  it('defines whitespace normalization helpers for online editor text matching drift', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /function\s+_buildNormalizedWhitespaceView\s*\(/,
      'Editor signer should define a normalized whitespace view helper for docs/office drift'
    );

    assert.match(
      signerCode,
      /\u00A0|NBSP|non-breaking/i,
      'Normalization strategy should explicitly account for non-breaking spaces'
    );

    assert.match(
      signerCode,
      /function\s+_findSingleNormalizedOccurrence\s*\(/,
      'Editor signer should define a normalized unique-match helper'
    );
  });

  it('uses normalized matching in online-editor embedding-plan fallback before giving up', () => {
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(
      signerCode,
      /_findSingleNormalizedOccurrence\(fullText,\s*visibleText\)/,
      'Online-editor fallback should use normalized matching for segmentation whitespace drift'
    );
  });
});
