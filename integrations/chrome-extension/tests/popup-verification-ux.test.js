import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Popup verification UX enhancements', () => {
  it('shows a dedicated revoked counter in verify summary', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');

    assert.match(
      popupHtml,
      /id="revoked-count"/,
      'Popup verify summary should include a revoked count slot'
    );
  });

  it('renders marker type metadata in verification detail items', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /detail\.markerType/,
      'Popup detail rendering should reference marker type metadata'
    );

    assert.match(
      popupJs,
      /markerLabel|markerTypeLabel/i,
      'Popup detail rendering should expose a marker type label for users'
    );
  });

  it('reads revoked counts from tab state when updating summary stats', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /revokedCountEl\.textContent\s*=\s*state\.revoked\s*\|\|\s*0/,
      'Popup summary updater should map tab-state revoked counter to UI'
    );
  });

  it('shows a clear authorship-proof detection headline and low-friction sign CTA on verify state', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');

    assert.match(
      popupHtml,
      /Verified authorship markers detected on this page/i,
      'Verify state should clearly call out when authorship proof is found'
    );

    assert.match(
      popupHtml,
      /id="verify-sign-cta"/,
      'Verify state should expose a low-friction CTA for users who want to sign their own content'
    );
  });

  it('renders a verification link in detail cards when a verification url or document reference exists', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /safeExternalUrl\(detail\.verificationUrl\)\s*\|\|\s*safeExternalUrl\(buildVerificationLink\(detail\.documentId\)\)/,
      'Popup detail rendering should resolve a verification URL for each verifiable item'
    );

    assert.match(
      popupJs,
      /View verification/i,
      'Popup detail cards should display a user-facing verification link label'
    );
  });

  it('supports click-to-scroll navigation from popup detail cards to page embeddings', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /detail\.detectionId/,
      'Popup detail rendering should carry detection IDs for page navigation'
    );

    assert.match(
      popupJs,
      /locateEmbeddingOnPage\(/,
      'Popup should expose a helper for locating a specific embedding on the page'
    );

    assert.match(
      popupJs,
      /type:\s*'FOCUS_EMBEDDING'/,
      'Popup should message the content script to focus a selected embedding'
    );
  });

  it('sanitizes verification URLs before rendering external links', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /function\s+safeExternalUrl\(/,
      'Popup should include a URL sanitizer helper for external links'
    );

    assert.match(
      popupJs,
      /parsed\.protocol\s*===\s*'http:'\s*\|\|\s*parsed\.protocol\s*===\s*'https:'/,
      'Popup should only allow http/https verification links'
    );
  });

  it('shows signed-content state when details exist even if count is zero', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /hasDetails\s*=\s*Array\.isArray\(state\.details\)\s*&&\s*state\.details\.length\s*>\s*0/,
      'Popup should detect detail-backed state independently of count'
    );

    assert.match(
      popupJs,
      /if\s*\(!state\s*\|\|\s*\(state\.count\s*===\s*0\s*&&\s*!hasDetails\s*&&\s*!hasImages\s*&&\s*!hasAudioVideo\)\)/,
      'Popup should only show empty state when count, details, images, and audio/video are all absent'
    );
  });
});
