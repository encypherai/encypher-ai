import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Popup branding + debug logging regressions', () => {
  it('uses white Encypher full logo and compact Verifier title in popup header', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');

    assert.match(
      popupHtml,
      /src="\.\.\/icons\/encypher_full_logo_white\.svg"/,
      'Popup header should use the white full Encypher logo asset'
    );

    assert.match(
      popupHtml,
      /<span class="popup__title">Verifier<\/span>/,
      'Popup header title should be compact and only show Verifier text'
    );
  });

  it('service worker excludes polling message types from debug log ingestion', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /GET_DEBUG_LOGS/,
      'Service worker should explicitly identify GET_DEBUG_LOGS as a noisy polling message'
    );

    assert.match(
      workerCode,
      /GET_TAB_STATE/,
      'Service worker should explicitly identify GET_TAB_STATE as a noisy polling message'
    );

    assert.match(
      workerCode,
      /if\s*\(![^\n]*\.has\(message\.type\)\)\s*\{\s*debugLog\.msg/s,
      'Service worker should guard debugLog.msg behind a message-type skip list'
    );
  });

  it('detector watches dynamic user edits and not just newly added nodes', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');

    assert.match(
      detectorCode,
      /characterData\s*:\s*true/,
      'MutationObserver should watch characterData mutations for in-place editor typing'
    );

    assert.match(
      detectorCode,
      /addEventListener\(\s*'input'/,
      'Detector should react to input events from WYSIWYG/contenteditable editing'
    );
  });
});
