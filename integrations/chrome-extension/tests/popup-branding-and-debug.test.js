import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Popup branding + debug logging regressions', () => {
  it('uses white Encypher full logo and compact Verify title in popup header', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');

    assert.match(
      popupHtml,
      /src="\.\.\/icons\/encypher_full_logo_white\.svg"/,
      'Popup header should use the white full Encypher logo asset'
    );

    assert.match(
      popupHtml,
      /<span class="popup__title">Verify<\/span>/,
      'Popup header title should be compact and only show Verify text'
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

  it('renders floating badges for editable surfaces to avoid writing badge markup into editor content', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');

    assert.match(
      detectorCode,
      /function\s+_isEditableSurface\(/,
      'Detector should detect editable surfaces before injecting verification badges'
    );

    assert.match(
      detectorCode,
      /document\.body\.appendChild\(badge\)/,
      'Editable-surface badges should be mounted on document.body as floating overlays'
    );

    assert.match(
      detectorCode,
      /if\s*\(editableSurface\)[\s\S]*return;[\s\S]*element\.appendChild\(badge\)/,
      'Detector should avoid inline badge insertion for editable surfaces while preserving inline mode for static content'
    );
  });

  it('skips wrapper-less C2PA fallback detections that commonly appear in transformed WYSIWYG mirror content', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');

    assert.match(
      detectorCode,
      /markerType\s*===\s*'c2pa'\s*&&\s*wrappers\.length\s*===\s*0/,
      'Detector should explicitly gate non-wrapper C2PA fallback candidates'
    );
  });

  it('treats WYSIWYG source/code panes as editable surfaces to avoid inline badge DOM pollution', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');
    const editableSurfaceFn = detectorCode.match(/function\s+_isEditableSurface\([\s\S]*?\n\}/)?.[0] || '';

    assert.match(
      editableSurfaceFn,
      /\.CodeMirror|\.cm-editor|\.ace_editor|\.tox-edit-area|\.mce-content-body/,
      'Detector should include source/code editor roots in editable-surface detection'
    );
  });

  it('renders Signing Identity row and clickable verification link in verification detail panel', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');

    assert.match(
      detectorCode,
      /Signing Identity/,
      'Detail panel should show Signing Identity instead of raw Organization label'
    );

    assert.match(
      detectorCode,
      /target="_blank"\s+rel="noopener"/,
      'Verification URL row should render as an external clickable link'
    );

    assert.match(
      detectorCode,
      /verificationUrl:\s*response\.data\?\.verification_url/,
      'Detector badge details should map verification_url from verify response data'
    );
  });

  it('exposes ENCYPHER_LOGO_SVG on globalThis so editor-signer can access it', () => {
    const detectorPath = path.join(EXTENSION_ROOT, 'content', 'detector.js');
    const detectorCode = fs.readFileSync(detectorPath, 'utf8');

    assert.match(
      detectorCode,
      /globalThis\.ENCYPHER_LOGO_SVG\s*=\s*ENCYPHER_LOGO_SVG/,
      'detector.js should assign ENCYPHER_LOGO_SVG to globalThis after declaration'
    );
  });

  it('inline sign button reads logo from globalThis.ENCYPHER_LOGO_SVG', () => {
    const editorSignerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const editorSignerCode = fs.readFileSync(editorSignerPath, 'utf8');

    assert.match(
      editorSignerCode,
      /globalThis\?\.ENCYPHER_LOGO_SVG/,
      'editor-signer.js createSignButton should read logo from globalThis.ENCYPHER_LOGO_SVG'
    );
  });

  it('signing UI modal header includes the Encypher logo', () => {
    const editorSignerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const editorSignerCode = fs.readFileSync(editorSignerPath, 'utf8');

    assert.match(
      editorSignerCode,
      /encypher-sign-ui__header-logo/,
      'Signing UI modal header should include a logo element with class encypher-sign-ui__header-logo'
    );

    assert.match(
      editorSignerCode,
      /encypher-sign-ui__header-brand/,
      'Signing UI modal header should wrap logo + title in a brand container'
    );
  });

  it('signing UI modal header logo CSS is defined', () => {
    const cssPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.css');
    const cssCode = fs.readFileSync(cssPath, 'utf8');

    assert.match(
      cssCode,
      /\.encypher-sign-ui__header-logo/,
      'editor-signer.css should define styles for the signing UI header logo'
    );

    assert.match(
      cssCode,
      /\.encypher-sign-ui__header-brand/,
      'editor-signer.css should define styles for the signing UI header brand wrapper'
    );
  });

  it('scans open shadow roots for editor surfaces so LinkedIn interop composer editors are discoverable', () => {
    const editorSignerPath = path.join(EXTENSION_ROOT, 'content', 'editor-signer.js');
    const editorSignerCode = fs.readFileSync(editorSignerPath, 'utf8');

    assert.match(
      editorSignerCode,
      /function\s+scanShadowRootsForEditors\(/,
      'Editor signer should define a dedicated shadow-root traversal helper'
    );

    assert.match(
      editorSignerCode,
      /if\s*\(el\.shadowRoot\)[\s\S]*scanForEditorsInRoot\(el\.shadowRoot\)/,
      'Shadow traversal should recurse through open shadow roots when scanning for editors'
    );

    assert.match(
      editorSignerCode,
      /node\.shadowRoot[\s\S]*scanForEditorsInRoot\(node\.shadowRoot\)/,
      'Mutation observer path should trigger scanning when newly added nodes host shadow roots'
    );
  });
});
