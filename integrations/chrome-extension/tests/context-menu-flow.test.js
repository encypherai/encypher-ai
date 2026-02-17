import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Context menu verify/sign flows', () => {
  it('registers verify and sign context menu entries for selected text', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(workerCode, /id:\s*'verify-selected-text'/);
    assert.match(workerCode, /id:\s*'sign-selected-text'/);
    assert.match(workerCode, /id:\s*'copy-signed-text'/);
  });

  it('routes verify selection from context menu with tab metadata for popup state/discovery', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /case\s+'verify-selected-text'[\s\S]*type:\s*'VERIFY_SELECTION'/,
      'Verify context action should dispatch VERIFY_SELECTION to the content script'
    );

    assert.match(
      workerCode,
      /pageUrl:\s*tab\.url\s*\|\|\s*''/,
      'Verify context action should include page URL metadata'
    );

    assert.match(
      workerCode,
      /pageTitle:\s*tab\.title\s*\|\|\s*''/,
      'Verify context action should include page title metadata'
    );

    assert.match(
      workerCode,
      /case\s+'verify-selected-text'[\s\S]*sendFrameMessageWithFallback\(tab\.id,\s*targetFrameId,[\s\S]*type:\s*'VERIFY_SELECTION'/,
      'Verify context action should target the originating frame so iframe/WYSIWYG selections are handled'
    );

    assert.match(
      workerCode,
      /case\s+'verify-selected-text'[\s\S]*requireAck:\s*true/,
      'Verify context action should require an explicit receiver acknowledgement to avoid silent no-op delivery'
    );
  });

  it('routes sign selection from context menu and handles missing tab context safely', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /if\s*\(!tab\?\.id\)\s*return;/,
      'Context menu handler should no-op when tab context is unavailable'
    );

    assert.match(
      workerCode,
      /case\s+'sign-selected-text'[\s\S]*type:\s*'SIGN_SELECTION'/,
      'Sign context action should dispatch SIGN_SELECTION to the content script'
    );

    assert.match(
      workerCode,
      /case\s+'sign-selected-text'[\s\S]*sendFrameMessageWithFallback\(tab\.id,\s*targetFrameId,[\s\S]*type:\s*'SIGN_SELECTION'/,
      'Sign context action should target the originating frame so selected-text replacement works in WYSIWYG iframes'
    );

    assert.match(
      workerCode,
      /case\s+'sign-selected-text'[\s\S]*requireAck:\s*true/,
      'Sign context action should require an explicit receiver acknowledgement so users do not see sign-start with no follow-up action'
    );

    assert.match(
      workerCode,
      /chrome\.scripting\.executeScript\([\s\S]*files:\s*CONTEXT_SCRIPT_FILES/,
      'Sign context action should attempt content-script injection fallback when no receiver exists in the target frame'
    );

    assert.match(
      workerCode,
      /Signing selected text\.\.\./,
      'Sign context action should show immediate in-page UX feedback while signing starts'
    );
  });

  it('injects content scripts into frames so WYSIWYG iframe panes are scanned and actionable', () => {
    const manifestPath = path.join(EXTENSION_ROOT, 'manifest.json');
    const manifestRaw = fs.readFileSync(manifestPath, 'utf8');
    const manifest = JSON.parse(manifestRaw);
    const contentScript = manifest.content_scripts?.[0] || {};

    assert.strictEqual(
      contentScript.all_frames,
      true,
      'Content scripts should run in all frames to cover editor iframes'
    );

    assert.strictEqual(
      contentScript.match_about_blank,
      true,
      'Content scripts should run in about:blank editor frames used by WYSIWYG surfaces'
    );
  });

  it('supports VERIFY_SELECTION and SIGN_SELECTION listeners in content scripts', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');
    const signerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const signerCode = fs.readFileSync(signerPath, 'utf8');

    assert.match(detectorCode, /message\.type\s*===\s*'VERIFY_SELECTION'/);
    assert.match(signerCode, /message\.type\s*===\s*'SIGN_SELECTION'/);
  });
});
