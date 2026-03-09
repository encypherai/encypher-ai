/**
 * Encypher Verify - Editor Signer
 *
 * Detects WYSIWYG editors and text containers on web pages,
 * providing inline signing capabilities for content creators.
 *
 * Supported editors:
 * - contenteditable elements
 * - textarea elements
 * - TinyMCE
 * - CKEditor
 * - Quill
 * - ProseMirror/Tiptap
 * - Draft.js (React)
 * - Medium Editor
 * - Froala
 * - Summernote
 */

// IIFE to avoid top-level const/let collisions with detector.js
// (both scripts share the same content-script scope)
(function () {

// Configuration
const EDITOR_CONFIG = {
  minTextLength: 10,
  debounceMs: 300,
  buttonGap: 12,
  viewportMargin: 16,
};

// Track signed content to avoid re-signing
const signedContentHashes = new Set();

// Track active editors
const activeEditors = new Map();

// Whether editor sign buttons are enabled (loaded from settings)
let editorButtonsEnabled = true;

// Signing option defaults (loaded from settings)
let defaultEmbeddingTechnique = 'micro';
let defaultSegmentationLevel = 'sentence';
let defaultDocumentType = 'article';
let defaultAutoReplaceContent = true;
let cachedAccountInfo = null;
let accountInfoPromise = null;
let primaryEditorId = null;
let editorObserverStarted = false;
const _observedShadowRoots = new WeakSet();

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function normalizeEmbeddingTechnique(value) {
  const mode = String(value || '').toLowerCase();
  if (mode === 'micro_ecc_c2pa' || mode === 'micro') return 'micro';
  if (mode === 'micro_ecc' || mode === 'micro_no_embed_c2pa') return 'micro_no_embed_c2pa';
  return 'micro';
}

// ── Embedding byte detection (mirrors detector.js constants) ──
const VS_RANGES = {
  VS1_START: 0xFE00, VS1_END: 0xFE0F,
  VS2_START: 0xE0100, VS2_END: 0xE01EF,
};
const ZWNBSP = 0xFEFF;

function _isVS(cp) {
  return (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) ||
         (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END);
}

function _isEmbeddingChar(cp) {
  return _isVS(cp) || cp === ZWNBSP;
}

/**
 * Find the full embedding run surrounding a cursor position in a string.
 * Returns { start, end } indices of the contiguous embedding byte run,
 * or null if the cursor is not adjacent to embedding bytes.
 */
function findEmbeddingRun(text, cursorPos) {
  const chars = [...text];
  if (cursorPos < 0 || cursorPos > chars.length) return null;

  // Check the character before and at the cursor
  let inRun = false;
  if (cursorPos > 0 && _isEmbeddingChar(chars[cursorPos - 1].codePointAt(0))) {
    inRun = true;
  }
  if (cursorPos < chars.length && _isEmbeddingChar(chars[cursorPos].codePointAt(0))) {
    inRun = true;
  }
  if (!inRun) return null;

  // Expand left
  let start = Math.min(cursorPos, chars.length - 1);
  if (start >= chars.length) start = chars.length - 1;
  while (start > 0 && _isEmbeddingChar(chars[start - 1].codePointAt(0))) {
    start--;
  }

  // Expand right
  let end = cursorPos;
  while (end < chars.length && _isEmbeddingChar(chars[end].codePointAt(0))) {
    end++;
  }

  if (end <= start) return null;
  return { start, end };
}

/**
 * Extract the raw embedding bytes from a substring of embedding characters.
 */
function extractRunBytes(text) {
  const bytes = [];
  for (const char of text) {
    const cp = char.codePointAt(0);
    if (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) {
      bytes.push(cp - VS_RANGES.VS1_START);
    } else if (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END) {
      bytes.push((cp - VS_RANGES.VS2_START) + 16);
    }
    // ZWNBSP is a prefix marker, not a data byte — skip
  }
  return bytes;
}

// ── Provenance chain storage ──
const PROVENANCE_KEY = 'encypher_provenance';
const PROVENANCE_MAX_ENTRIES = 50;

/**
 * Store an embedding's bytes as provenance before it is deleted or replaced.
 * Keyed by a hash of the visible text that contained the embedding.
 */
async function storeProvenance(visibleTextHash, embeddingBytes, metadata = {}) {
  try {
    const result = await chrome.storage.local.get({ [PROVENANCE_KEY]: {} });
    const store = result[PROVENANCE_KEY] || {};

    if (!store[visibleTextHash]) {
      store[visibleTextHash] = [];
    }

    store[visibleTextHash].push({
      bytes: Array.from(embeddingBytes),
      timestamp: Date.now(),
      url: window.location.href,
      ...metadata
    });

    // Cap per-key entries
    if (store[visibleTextHash].length > 10) {
      store[visibleTextHash] = store[visibleTextHash].slice(-10);
    }

    // Cap total keys
    const keys = Object.keys(store);
    if (keys.length > PROVENANCE_MAX_ENTRIES) {
      // Remove oldest entries
      const sorted = keys.sort((a, b) => {
        const aTime = store[a][store[a].length - 1]?.timestamp || 0;
        const bTime = store[b][store[b].length - 1]?.timestamp || 0;
        return aTime - bTime;
      });
      for (let i = 0; i < keys.length - PROVENANCE_MAX_ENTRIES; i++) {
        delete store[sorted[i]];
      }
    }

    await chrome.storage.local.set({ [PROVENANCE_KEY]: store });
  } catch (e) {
    // Storage errors are non-fatal
  }
}

/**
 * Retrieve provenance chain for content identified by its visible text hash.
 */
async function getProvenance(visibleTextHash) {
  try {
    const result = await chrome.storage.local.get({ [PROVENANCE_KEY]: {} });
    return (result[PROVENANCE_KEY] || {})[visibleTextHash] || [];
  } catch (e) {
    return [];
  }
}

/**
 * Detect which online editor platform we're on (if any)
 */
function detectOnlinePlatform() {
  const hostname = window.location.hostname;
  const pathname = window.location.pathname;

  // Google Docs
  if (hostname === 'docs.google.com' && pathname.startsWith('/document/')) {
    return 'google-docs';
  }

  // Microsoft Word Online
  if (
    (hostname === 'word.live.com' || hostname.endsWith('.officeapps.live.com')) ||
    (hostname.endsWith('.sharepoint.com') && pathname.includes('/_layouts/15/Doc.aspx'))
  ) {
    return 'ms-word-online';
  }

  return null;
}

/**
 * Get the main editable region for an online platform.
 * Returns { element, type } or null.
 */
function getOnlineEditorElement(platform) {
  switch (platform) {
    case 'google-docs': {
      // Google Docs renders via canvas but exposes an accessibility layer
      // with contenteditable .kix-appview-editor or the iframe body.
      const kixEditor = document.querySelector('.kix-appview-editor');
      if (kixEditor) return { element: kixEditor, type: 'google-docs' };
      // Fallback: the page content wrapper
      const pageContent = document.querySelector('.kix-page-content-wrapper');
      if (pageContent) return { element: pageContent, type: 'google-docs' };
      return null;
    }
    case 'ms-word-online': {
      // Word Online uses a contenteditable div inside WACViewPanel
      const canvas = document.querySelector('[data-content-type="RichText"][contenteditable="true"]');
      if (canvas) return { element: canvas, type: 'ms-word-online' };
      // Fallback: the main editing surface
      const surface = document.querySelector('.WACViewPanel_EditingElement');
      if (surface) return { element: surface, type: 'ms-word-online' };
      const ce = document.querySelector('#WACViewPanel [contenteditable="true"]');
      if (ce) return { element: ce, type: 'ms-word-online' };
      return null;
    }
    default:
      return null;
  }
}

/**
 * Simple hash for content tracking
 */
function hashText(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}

/**
 * Detect editor type from element
 */
function detectEditorType(element) {
  // Check for specific editor frameworks
  const parent = element.parentElement;

  // Google Docs
  if (element.classList.contains('kix-appview-editor') ||
      element.classList.contains('kix-page-content-wrapper')) {
    return 'google-docs';
  }

  // Microsoft Word Online
  if (element.getAttribute('data-content-type') === 'RichText' ||
      element.classList.contains('WACViewPanel_EditingElement')) {
    return 'ms-word-online';
  }

  // TinyMCE
  if (element.classList.contains('mce-content-body') ||
      parent?.classList.contains('tox-edit-area') ||
      element.id?.startsWith('tinymce')) {
    return 'tinymce';
  }

  // CKEditor
  if (element.classList.contains('ck-editor__editable') ||
      element.classList.contains('cke_editable') ||
      parent?.classList.contains('ck-editor')) {
    return 'ckeditor';
  }

  // Quill
  if (element.classList.contains('ql-editor') ||
      parent?.classList.contains('ql-container')) {
    return 'quill';
  }

  // ProseMirror / Tiptap
  if (element.classList.contains('ProseMirror') ||
      element.classList.contains('tiptap')) {
    return 'prosemirror';
  }

  // Draft.js
  if (element.classList.contains('DraftEditor-root') ||
      element.classList.contains('public-DraftEditor-content') ||
      element.getAttribute('data-contents') === 'true') {
    return 'draftjs';
  }

  // Medium Editor
  if (element.classList.contains('medium-editor-element') ||
      element.getAttribute('data-medium-editor-element') === 'true') {
    return 'medium';
  }

  // Froala
  if (element.classList.contains('fr-element') ||
      parent?.classList.contains('fr-wrapper')) {
    return 'froala';
  }

  // Summernote
  if (element.classList.contains('note-editable') ||
      parent?.classList.contains('note-editor')) {
    return 'summernote';
  }

  // Generic contenteditable
  if (element.isContentEditable || element.getAttribute('contenteditable') === 'true') {
    return 'contenteditable';
  }

  // Textarea
  if (element.tagName === 'TEXTAREA') {
    return 'textarea';
  }

  // Input (text type)
  if (element.tagName === 'INPUT' &&
      ['text', 'search', ''].includes(element.type)) {
    return 'input';
  }

  return null;
}

/**
 * Get text content from editor element
 */
function getEditorText(element, editorType) {
  switch (editorType) {
    case 'textarea':
    case 'input':
      return element.value || '';

    case 'google-docs': {
      // Google Docs: extract text from the accessibility layer.
      // The .kix-lineview spans contain the visible text.
      const lines = element.querySelectorAll('.kix-lineview');
      if (lines.length > 0) {
        return Array.from(lines).map(l => l.textContent || '').join('\n');
      }
      // Fallback: all paragraph content wrappers
      const paragraphs = element.querySelectorAll('.kix-paragraphrenderer');
      if (paragraphs.length > 0) {
        return Array.from(paragraphs).map(p => p.textContent || '').join('\n');
      }
      return element.innerText || element.textContent || '';
    }

    case 'ms-word-online':
      return element.innerText || element.textContent || '';

    case 'tinymce':
      // Try to get TinyMCE instance
      if (typeof tinymce !== 'undefined') {
        const editor = tinymce.get(element.id);
        if (editor) return editor.getContent({ format: 'text' });
      }
      return element.innerText || element.textContent || '';

    case 'ckeditor':
      // Try to get CKEditor instance
      if (typeof CKEDITOR !== 'undefined' && element.id) {
        const editor = CKEDITOR.instances[element.id];
        if (editor) return editor.getData();
      }
      return element.innerText || element.textContent || '';

    case 'quill': {
      // Quill stores instance on parent
      const quillContainer = element.closest('.ql-container');
      if (quillContainer?.__quill) {
        return quillContainer.__quill.getText();
      }
      return element.innerText || element.textContent || '';
    }

    default:
      return element.innerText || element.textContent || '';
  }
}

/**
 * Set text content in editor element.
 * For Google Docs and MS Word Online, we copy to clipboard instead of
 * modifying the DOM directly (their internal models would desync).
 */
function setEditorText(element, editorType, text) {
  switch (editorType) {
    case 'textarea':
    case 'input':
      element.value = text;
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      break;

    case 'google-docs':
    case 'ms-word-online':
      // Cannot safely mutate the DOM of these editors.
      // Copy signed text to clipboard so the user can paste it.
      navigator.clipboard.writeText(text).then(() => {
        showNotification('info', 'Signed text copied to clipboard. Paste (Ctrl+V) to replace content.');
      }).catch(() => {
        showNotification('error', 'Could not copy to clipboard.');
      });
      return;

    case 'tinymce':
      if (typeof tinymce !== 'undefined') {
        const editor = tinymce.get(element.id);
        if (editor) {
          editor.setContent(text);
          return;
        }
      }
      element.innerText = text;
      break;

    case 'ckeditor':
      if (typeof CKEDITOR !== 'undefined' && element.id) {
        const editor = CKEDITOR.instances[element.id];
        if (editor) {
          editor.setData(text);
          return;
        }
      }
      element.innerText = text;
      break;

    case 'quill': {
      const quillContainer = element.closest('.ql-container');
      if (quillContainer?.__quill) {
        quillContainer.__quill.setText(text);
        return;
      }
      element.innerText = text;
      break;
    }

    default:
      element.innerText = text;
      // Trigger input event for frameworks
      element.dispatchEvent(new Event('input', { bubbles: true }));
  }
 }

/**
 * Create the Encypher sign button
 */
function createSignButton(editorId) {
  const button = document.createElement('button');
  button.className = 'encypher-sign-btn encypher-sign-btn--compact';
  button.id = `encypher-sign-${editorId}`;
  button.setAttribute('type', 'button');
  button.setAttribute('aria-label', 'Sign content with Encypher');
  button.setAttribute('title', 'Quick sign with Encypher · Shift-click for options');

  // Use the Encypher logo (defined in detector.js, which loads first in the
  // same content-script group).  Fall back to a simple shield if unavailable.
  const sharedLogoSvg = typeof globalThis?.ENCYPHER_LOGO_SVG === 'string'
    ? globalThis.ENCYPHER_LOGO_SVG
    : null;
  const logoSvg = sharedLogoSvg
    ? sharedLogoSvg
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>';

  button.innerHTML = `
    <span class="encypher-sign-btn__icon">${logoSvg}</span>
    <span class="encypher-sign-btn__text">Sign</span>
  `;

  return button;
}

function showNotification(type, message) {
  const existing = document.querySelector('.encypher-notification');
  existing?.remove();

  const notification = document.createElement('div');
  notification.className = `encypher-notification encypher-notification--${type}`;
  notification.innerHTML = `
    <div class="encypher-notification__icon">${type === 'success' ? '✓' : type === 'error' ? '!' : 'i'}</div>
    <div class="encypher-notification__content">${escapeHtml(String(message || ''))}</div>
  `;
  document.body.appendChild(notification);

  window.setTimeout(() => {
    notification.style.opacity = '0';
    window.setTimeout(() => notification.remove(), 300);
  }, 3200);
}

function setPrimaryEditor(editorId) {
  primaryEditorId = editorId;
  for (const [, info] of activeEditors) {
    info.updateVisibility?.();
  }
}

function positionButton(button, editor) {
  if (!button?.isConnected || !editor?.isConnected || button.dataset.hosted === 'true') return;

  const editorRect = editor.getBoundingClientRect();
  const margin = EDITOR_CONFIG.viewportMargin;
  const gap = EDITOR_CONFIG.buttonGap;
  const buttonWidth = button.offsetWidth || 110;
  const buttonHeight = button.offsetHeight || 36;
  let top = editorRect.top - buttonHeight - gap;

  if (top < margin) {
    top = editorRect.bottom + gap;
  }

  const maxTop = Math.max(margin, window.innerHeight - margin - buttonHeight);
  const maxLeft = Math.max(margin, window.innerWidth - margin - buttonWidth);
  const left = clamp(editorRect.right - buttonWidth, margin, maxLeft);

  button.style.position = 'fixed';
  button.style.top = `${clamp(top, margin, maxTop)}px`;
  button.style.left = `${left}px`;
  button.style.right = 'auto';
  button.style.bottom = 'auto';
  button.style.zIndex = '10001';
}

function createRepositionScheduler(button, editor) {
  let frameId = null;

  return function scheduleReposition() {
    if (frameId !== null) return;
    frameId = requestAnimationFrame(() => {
      frameId = null;
      if (!button.isConnected || !editor.isConnected) return;
      positionButton(button, editor);
    });
  };
}

function positionSigningUI(ui, button) {
  const buttonRect = button.getBoundingClientRect();
  const margin = EDITOR_CONFIG.viewportMargin;
  const gap = 8;
  const uiRect = ui.getBoundingClientRect();
  const maxLeft = Math.max(margin, window.innerWidth - margin - uiRect.width);
  const maxTop = Math.max(margin, window.innerHeight - margin - uiRect.height);
  let top = buttonRect.bottom + gap;

  if (top + uiRect.height > window.innerHeight - margin) {
    top = buttonRect.top - uiRect.height - gap;
  }

  top = clamp(top, margin, maxTop);
  const left = clamp(buttonRect.right - uiRect.width, margin, maxLeft);

  ui.style.position = 'fixed';
  ui.style.top = `${top}px`;
  ui.style.left = `${left}px`;
  ui.style.right = 'auto';
}

function showSigningUI(editor, editorType, button) {
  document.querySelector('.encypher-sign-ui')?.remove();

  const editorId = button.id.replace('encypher-sign-', '');
  const ui = document.createElement('div');
  ui.className = 'encypher-sign-ui';
  ui.dataset.editorId = editorId;

  const text = getEditorText(editor, editorType) || '';
  const preview = text.trim().slice(0, 240);
  const signerLabel = getSignerLabel(cachedAccountInfo);

  ui.innerHTML = `
    <div class="encypher-sign-ui__header">
      <div class="encypher-sign-ui__header-brand">
        <span class="encypher-sign-ui__header-logo">${typeof globalThis?.ENCYPHER_LOGO_SVG === 'string' ? globalThis.ENCYPHER_LOGO_SVG : ''}</span>
        <h3>Sign content</h3>
      </div>
      <button type="button" class="encypher-sign-ui__close" aria-label="Close">×</button>
    </div>
    <div class="encypher-sign-ui__body">
      <div class="encypher-sign-ui__identity">Signing as: ${escapeHtml(signerLabel)}</div>
      <div class="encypher-sign-ui__trust">Invisible proof of origin is embedded into your text and can be verified later.</div>
      <div class="encypher-sign-ui__preview">
        <label>Preview</label>
        <div class="encypher-sign-ui__text">${escapeHtml(preview || 'No content to preview yet.')}</div>
        <div class="encypher-sign-ui__meta">${text.trim().length} characters</div>
      </div>
      <div class="encypher-sign-ui__shortcut">Shortcut: ${escapeHtml(getShortcutHint())}</div>
      <button type="button" class="encypher-sign-ui__toggle">Advanced options</button>
      <div class="encypher-sign-ui__advanced" hidden>
        <div class="encypher-sign-ui__select-group">
          <label for="encypher-manifest-mode">Proof mode</label>
          <select id="encypher-manifest-mode" class="encypher-sign-ui__select">
            <option value="micro">Embedded</option>
            <option value="micro_no_embed_c2pa">Compact</option>
          </select>
        </div>
        <div class="encypher-sign-ui__select-group">
          <label for="encypher-segmentation-level">Frequency</label>
          <select id="encypher-segmentation-level" class="encypher-sign-ui__select">
            <option value="sentence">Sentence</option>
            <option value="paragraph">Paragraph</option>
            <option value="document">Document</option>
          </select>
        </div>
        <div class="encypher-sign-ui__select-group">
          <label for="encypher-document-type">Document type</label>
          <select id="encypher-document-type" class="encypher-sign-ui__select">
            <option value="article">Article</option>
            <option value="social">Social</option>
            <option value="email">Email</option>
            <option value="message">Message</option>
          </select>
        </div>
        <div class="encypher-sign-ui__options">
          <label><input type="checkbox" id="encypher-replace-content"> Replace editor content after signing</label>
        </div>
      </div>
    </div>
    <div class="encypher-sign-ui__footer">
      <button type="button" class="encypher-sign-ui__btn encypher-sign-ui__btn--secondary">Cancel</button>
      <button type="button" class="encypher-sign-ui__btn encypher-sign-ui__btn--primary">
        <span class="encypher-sign-ui__btn-label">Sign now</span>
        <span class="encypher-sign-ui__btn-loading">Signing…</span>
      </button>
    </div>
  `;

  document.body.appendChild(ui);
  const advancedToggle = ui.querySelector('.encypher-sign-ui__toggle');
  const advancedPanel = ui.querySelector('.encypher-sign-ui__advanced');
  const closeButton = ui.querySelector('.encypher-sign-ui__close');
  const cancelButton = ui.querySelector('.encypher-sign-ui__btn--secondary');
  const primaryButton = ui.querySelector('.encypher-sign-ui__btn--primary');
  const loading = ui.querySelector('.encypher-sign-ui__btn-loading');
  const label = ui.querySelector('.encypher-sign-ui__btn-label');
  const manifestSelect = ui.querySelector('#encypher-manifest-mode');
  const segmentationSelect = ui.querySelector('#encypher-segmentation-level');
  const documentTypeSelect = ui.querySelector('#encypher-document-type');
  const replaceCheckbox = ui.querySelector('#encypher-replace-content');

  manifestSelect.value = defaultEmbeddingTechnique;
  segmentationSelect.value = defaultSegmentationLevel;
  documentTypeSelect.value = defaultDocumentType;
  replaceCheckbox.checked = defaultAutoReplaceContent;

  const cleanup = () => {
    document.removeEventListener('mousedown', handleOutsideClick, true);
    window.removeEventListener('resize', reposition, { passive: true });
    window.removeEventListener('scroll', reposition, { passive: true });
    ui.remove();
    activeEditors.get(editorId)?.updateVisibility?.();
  };

  const reposition = () => positionSigningUI(ui, button);
  const handleOutsideClick = (event) => {
    if (ui.contains(event.target) || button.contains(event.target)) return;
    cleanup();
  };

  advancedToggle.addEventListener('click', () => {
    const nextHidden = !advancedPanel.hidden;
    advancedPanel.hidden = nextHidden;
    advancedToggle.textContent = nextHidden ? 'Advanced options' : 'Hide advanced options';
    reposition();
  });

  closeButton.addEventListener('click', cleanup);
  cancelButton.addEventListener('click', cleanup);
  primaryButton.addEventListener('click', async () => {
    primaryButton.disabled = true;
    label.style.display = 'none';
    loading.classList.add('encypher-sign-ui__btn-loading--active');
    try {
      const result = await signEditorContent({
        editor,
        editorType,
        button,
        replaceContent: replaceCheckbox.checked,
        manifestMode: manifestSelect.value,
        segmentationLevel: segmentationSelect.value,
        documentType: documentTypeSelect.value,
      });
      const verificationUrl = result?.verificationUrl;
      const documentId = result?.documentId;
      ui.querySelector('.encypher-sign-ui__body').innerHTML = `
        <div class="encypher-sign-ui__success-badge">✓ Signed successfully</div>
        <div class="encypher-sign-ui__identity">Signed as: ${escapeHtml(getSignerLabel(cachedAccountInfo))}</div>
        <div class="encypher-sign-ui__trust">Your content now includes invisible proof of origin.</div>
        <div class="encypher-sign-ui__meta-row"><span>Document ID</span><strong>${escapeHtml(documentId || 'Available after verification')}</strong></div>
        ${verificationUrl ? `<a class="encypher-sign-ui__link" href="${escapeHtml(verificationUrl)}" target="_blank" rel="noreferrer">Open verification details</a>` : ''}
      `;
      ui.querySelector('.encypher-sign-ui__footer').innerHTML = `
        <button type="button" class="encypher-sign-ui__btn encypher-sign-ui__btn--primary">Done</button>
      `;
      ui.querySelector('.encypher-sign-ui__btn--primary')?.addEventListener('click', cleanup);
      reposition();
    } catch (error) {
      showNotification('error', error.message || 'Signing error');
      primaryButton.disabled = false;
      label.style.display = '';
      loading.classList.remove('encypher-sign-ui__btn-loading--active');
    }
  });

  document.addEventListener('mousedown', handleOutsideClick, true);
  window.addEventListener('resize', reposition, { passive: true });
  window.addEventListener('scroll', reposition, { passive: true });
  getCachedAccountInfo().then(() => {
    const identityEl = ui.querySelector('.encypher-sign-ui__identity');
    if (identityEl) {
      identityEl.textContent = `Signing as: ${getSignerLabel(cachedAccountInfo)}`;
    }
  });
  reposition();
}

function _attachEmbeddingRunHandlers() {
}

function getSiteAdapter(editor) {
  const hostname = window.location.hostname;

  if (hostname === 'github.com') {
    const issueCreateButton = document.querySelector('button[data-testid="create-issue-button"]');
    const issueActionContainer = issueCreateButton?.closest('[class*="actionButtonsContainer"]');
    const issueFooterChildren = document.querySelector('[data-testid="markdown-editor-footer"] [class*="childrenStyling"]');
    if (editor.matches?.('textarea[aria-label="Markdown value"], textarea[placeholder="Type your description here…"]')) {
      return {
        key: 'github-issue',
        tryAttach(button) {
          if (issueActionContainer && issueCreateButton && !issueActionContainer.contains(button)) {
            issueActionContainer.insertBefore(button, issueCreateButton);
            return true;
          }
          if (issueFooterChildren && !issueFooterChildren.contains(button)) {
            issueFooterChildren.appendChild(button);
            return true;
          }
          return false;
        }
      };
    }

    const commentContainer = editor.closest?.('[class*="MarkdownEditor-module__container"]')
      || editor.closest?.('[class*="js-slash-command-surface"]')
      || document;
    const commentTooltip = commentContainer.querySelector('span[data-testid="save-button-tooltip"]');
    const commentButton = commentTooltip?.querySelector('button');
    const commentFooter = commentTooltip?.closest('[data-testid="markdown-editor-footer"]')
      || commentContainer.querySelector('[data-testid="markdown-editor-footer"]');
    const commentChildrenArea = commentFooter?.querySelector('[class*="childrenStyling"]');
    if (editor.matches?.('textarea[placeholder="Use Markdown to format your comment"], textarea[placeholder*="Markdown"]')) {
      return {
        key: 'github-comment',
        tryAttach(button) {
          if (commentChildrenArea && commentTooltip && !commentChildrenArea.contains(button)) {
            commentChildrenArea.insertBefore(button, commentTooltip);
            return true;
          }
          if (commentFooter && commentButton && !commentFooter.contains(button)) {
            commentFooter.appendChild(button);
            return true;
          }
          return false;
        }
      };
    }
  }

  if (hostname === 'x.com' || hostname === 'twitter.com') {
    const composeDialog = editor.closest?.('div[role="dialog"]') || document;
    const tweetButton = composeDialog.querySelector('button[data-testid="tweetButtonInline"]');
    const tweetButtonCluster = tweetButton?.parentElement;
    const toolbarNav = composeDialog.querySelector('div[data-testid="toolBar"] nav');
    if (editor.matches?.('div[data-testid^="tweetTextarea_"][role="textbox"], div[data-testid="tweetTextarea_0"]')) {
      return {
        key: 'x-post',
        tryAttach(button) {
          if (tweetButtonCluster && tweetButton && !tweetButtonCluster.contains(button)) {
            tweetButtonCluster.insertBefore(button, tweetButton);
            return true;
          }
          if (toolbarNav && !toolbarNav.contains(button)) {
            toolbarNav.appendChild(button);
            return true;
          }
          return false;
        }
      };
    }
  }

  if (hostname === 'medium.com') {
    const publishButton = document.querySelector('button.button--primary.button--filled');
    const publishContainer = publishButton?.parentElement;
    const metabarActions = document.querySelector('div.metabar-block.u-flex0 .u-flexCenter')
      || document.querySelector('div.metabar-block.u-flex0');
    if (editor.matches?.('div.postArticle-content.js-postField, div[role="textbox"].postArticle-content')) {
      return {
        key: 'medium-story',
        tryAttach(button) {
          if (publishContainer && publishButton && !publishContainer.contains(button)) {
            publishContainer.insertBefore(button, publishButton);
            return true;
          }
          if (metabarActions && !metabarActions.contains(button)) {
            metabarActions.appendChild(button);
            return true;
          }
          return false;
        }
      };
    }
  }

  if (hostname === 'www.linkedin.com' || hostname === 'linkedin.com') {
    const interopOutlet = document.getElementById('interop-outlet');
    const shadowRoot = interopOutlet?.shadowRoot || null;
    const root = editor?.getRootNode?.();

    if (shadowRoot && root === shadowRoot) {
      const postButton = shadowRoot.querySelector('button.share-actions__primary-action');
      const postContainer = postButton?.parentElement;
      const schedulePostContainer = shadowRoot.querySelector('.share-creation-state__schedule-and-post-container');
      const messageSendButton = editor.closest?.('form[id*="msg-form"]')?.querySelector('button.msg-form__send-button')
        || shadowRoot.querySelector('button.msg-form__send-button');
      const messageActions = messageSendButton?.closest('.msg-form__right-actions');
      const messageFooter = editor.closest?.('form[id*="msg-form"]')?.querySelector('footer.msg-form__footer')
        || shadowRoot.querySelector('footer.msg-form__footer');

      if (editor.matches?.('[aria-label="Text editor for creating content"][role="textbox"], div.ql-editor[role="textbox"]')) {
        return {
          key: 'linkedin-post',
          tryAttach(button) {
            if (postContainer && postButton && !postContainer.contains(button)) {
              postContainer.insertBefore(button, postButton);
              return true;
            }
            if (schedulePostContainer && !schedulePostContainer.contains(button)) {
              schedulePostContainer.prepend(button);
              return true;
            }
            return false;
          }
        };
      }

      if (editor.matches?.('div.msg-form__contenteditable[role="textbox"], [aria-label="Write a message…"][role="textbox"]')) {
        return {
          key: 'linkedin-message',
          tryAttach(button) {
            if (messageActions && messageSendButton && !messageActions.contains(button)) {
              messageActions.insertBefore(button, messageSendButton);
              return true;
            }
            if (messageFooter && !messageFooter.contains(button)) {
              messageFooter.appendChild(button);
              return true;
            }
            return false;
          }
        };
      }
    }

    const articleNextButton = document.querySelector('button.article-editor-nav__publish');
    const articleNavActions = articleNextButton?.parentElement;
    const articleToolbar = document.querySelector('div.article-editor-toolbar');
    if (editor.matches?.('[aria-label="Article editor content"][role="textbox"], div.ProseMirror[role="textbox"]')) {
      return {
        key: 'linkedin-article',
        tryAttach(button) {
          if (articleNavActions && articleNextButton && !articleNavActions.contains(button)) {
            articleNavActions.insertBefore(button, articleNextButton);
            return true;
          }
          if (articleToolbar && !articleToolbar.contains(button)) {
            articleToolbar.appendChild(button);
            return true;
          }
          return false;
        }
      };
    }
  }

  if (hostname === 'chatgpt.com' || hostname === 'chat.openai.com') {
    const threadBottom = document.querySelector('#thread-bottom-container');
    const sendButton = threadBottom?.querySelector('[data-testid="send-button"]');
    const footerActions = threadBottom?.querySelector('[data-testid="composer-footer-actions"]');
    return {
      key: 'chatgpt',
      tryAttach(button) {
        const cluster = sendButton?.parentElement;
        if (cluster && sendButton && !cluster.contains(button)) {
          cluster.insertBefore(button, sendButton);
          return true;
        }
        if (footerActions && !footerActions.contains(button)) {
          footerActions.appendChild(button);
          return true;
        }
        return false;
      }
    };
  }

  if (hostname === 'claude.ai') {
    const container = document.querySelector('[data-testid="chat-input-grid-container"]');
    const sendButton = container?.querySelector('button[aria-label="Send message"]');
    const rightCluster = sendButton?.closest('.shrink-0.flex.items-center') || sendButton?.parentElement;
    const leftCluster = container?.querySelector('[data-testid="model-selector-dropdown"]')?.closest('.relative.flex-1');
    return {
      key: 'claude',
      tryAttach(button) {
        if (rightCluster && sendButton && !rightCluster.contains(button)) {
          rightCluster.insertBefore(button, sendButton);
          return true;
        }
        if (leftCluster && !leftCluster.contains(button)) {
          leftCluster.appendChild(button);
          return true;
        }
        return false;
      }
    };
  }

  if (hostname === 'mail.google.com') {
    const composeRegion = editor?.closest?.('[role="region"][aria-label="New Message"]');
    const formattingToolbar = composeRegion?.querySelector('[role="toolbar"][aria-label="Formatting options"]');
    const sendButton = composeRegion?.querySelector('[role="button"][data-tooltip*="Send"], [role="button"][aria-label*="Send"]');
    return {
      key: 'gmail',
      tryAttach(button) {
        if (formattingToolbar && isElementVisible(formattingToolbar) && !formattingToolbar.contains(button)) {
          formattingToolbar.appendChild(button);
          return true;
        }
        const sendCell = sendButton?.closest('td');
        const sendRow = sendCell?.parentElement;
        if (sendCell && sendRow && !sendRow.contains(button)) {
          const hostCell = document.createElement('td');
          hostCell.className = sendCell.className || 'gU';
          hostCell.appendChild(button);
          sendRow.insertBefore(hostCell, sendCell);
          return true;
        }
        return false;
      }
    };
  }

  if (hostname === 'outlook.live.com' || hostname === 'outlook.office.com') {
    const sendContainer = document.querySelector('[data-testid="ComposeSendButton"]');
    const actionRow = sendContainer?.parentElement;
    return {
      key: 'outlook',
      tryAttach(button) {
        if (actionRow && sendContainer && !actionRow.contains(button)) {
          actionRow.insertBefore(button, sendContainer);
          return true;
        }
        return false;
      }
    };
  }

  if (hostname === 'app.slack.com') {
    const suffix = document.querySelector('[data-qa="wysiwyg-container_suffix"]');
    const sendButton = suffix?.querySelector('[data-qa="texty_send_button"]');
    const sendCluster = sendButton?.parentElement || suffix;
    const toolbarButtons = document.querySelector('[data-qa="wysiwyg-container_toolbar-buttons"] .c-texty_buttons')
      || document.querySelector('[data-qa="wysiwyg-container_toolbar-buttons"]');
    return {
      key: 'slack',
      tryAttach(button) {
        if (sendCluster && sendButton && !sendCluster.contains(button)) {
          sendCluster.insertBefore(button, sendButton);
          return true;
        }
        if (toolbarButtons && !toolbarButtons.contains(button)) {
          toolbarButtons.appendChild(button);
          return true;
        }
        return false;
      }
    };
  }

  return null;
}

function attachButtonToPreferredHost(button, editor) {
  const adapter = getSiteAdapter(editor);
  if (!adapter) return false;

  const attached = adapter.tryAttach(button);
  if (attached) {
    button.dataset.hosted = 'true';
    button.dataset.hostKind = adapter.key;
    button.classList.add('encypher-sign-btn--hosted', 'encypher-sign-btn--visible', 'encypher-sign-btn--expanded');
    button.style.position = 'relative';
    button.style.top = 'auto';
    button.style.left = 'auto';
    button.style.right = 'auto';
    button.style.bottom = 'auto';
    button.style.zIndex = 'auto';
    return true;
  }

  button.dataset.hosted = 'false';
  button.dataset.hostKind = 'floating';
  button.classList.remove('encypher-sign-btn--hosted');
  ensureButtonMountedInBody(button);
  return false;
}

function ensureButtonMountedInBody(button) {
  if (button.parentElement !== document.body) {
    document.body.appendChild(button);
  }
}

function shouldPreferHostedPlacement(editor) {
  const hostname = window.location.hostname;
  return hostname === 'github.com'
    || hostname === 'x.com'
    || hostname === 'twitter.com'
    || hostname === 'medium.com'
    || hostname === 'chatgpt.com'
    || hostname === 'chat.openai.com'
    || hostname === 'claude.ai'
    || hostname === 'www.linkedin.com'
    || hostname === 'linkedin.com'
    || hostname === 'mail.google.com'
    || hostname === 'outlook.live.com'
    || hostname === 'outlook.office.com'
    || hostname === 'app.slack.com';
}

function updateButtonPresentation(button, options = {}) {
  const signed = Boolean(options.signed);
  const ready = Boolean(options.ready) && !signed;
  const compact = options.surface !== 'document';
  const buttonText = button.querySelector('.encypher-sign-btn__text');
  if (buttonText) {
    buttonText.textContent = signed ? 'Signed' : 'Sign';
  }
  button.classList.toggle('encypher-sign-btn--signed', signed);
  button.classList.toggle('encypher-sign-btn--ready', ready);
  button.classList.toggle('encypher-sign-btn--compact', compact);
  button.dataset.surface = options.surface || 'generic';
  button.setAttribute('aria-label', signed ? 'Signed content with Encypher' : (ready ? 'Quick sign content with Encypher' : 'Sign content with Encypher'));
  button.setAttribute('title', signed ? 'Signed with Encypher · Click for details' : (ready ? 'Quick sign with Encypher · Shift-click for options' : 'Sign with Encypher · Shift-click for options'));
}

function updateEditorButtonState(info, options = {}) {
  if (!info?.button || !info?.element?.isConnected) return;
  const text = getEditorText(info.element, info.type) || '';
  const trimmedLength = text.trim().length;
  const ready = trimmedLength >= EDITOR_CONFIG.minTextLength;
  const ui = document.querySelector('.encypher-sign-ui');
  const keepVisible = ui?.dataset.editorId === info.editorId;
  const active = primaryEditorId === info.editorId;
  const visible = info.isOnlineEditor || keepVisible || options.forceVisible || active || Boolean(info.insideModal && trimmedLength > 0);
  updateButtonPresentation(info.button, {
    ready,
    signed: info.button.classList.contains('encypher-sign-btn--signed'),
    surface: info.surface
  });
  const hosted = info.button.dataset.hosted === 'true';
  info.button.classList.toggle('encypher-sign-btn--visible', hosted || visible);
  info.button.classList.toggle('encypher-sign-btn--expanded', hosted || Boolean(visible && (options.expanded || keepVisible)));
}

async function signEditorContent(options) {
  const editor = options.editor;
  const editorType = options.editorType;
  const button = options.button;
  const text = getEditorText(editor, editorType);
  if ((text || '').trim().length < EDITOR_CONFIG.minTextLength) {
    showNotification('error', 'Content too short to sign (minimum 10 characters)');
    return null;
  }

  const response = await chrome.runtime.sendMessage({
    type: 'SIGN_CONTENT',
    text,
    title: options.title || undefined,
    options: {
      manifestMode: options.manifestMode || defaultEmbeddingTechnique,
      segmentationLevel: options.segmentationLevel || defaultSegmentationLevel,
      documentType: options.documentType || defaultDocumentType,
    }
  });

  if (!response?.success) {
    throw new Error(response?.error || 'Signing failed');
  }

  if (options.replaceContent) {
    const applied = response.embeddingPlan
      ? applyEmbeddingPlanToEditorInPlace(editor, editorType, response.embeddingPlan, text)
      : false;
    if (!applied) {
      setEditorText(editor, editorType, response.signedText);
    }
  }

  signedContentHashes.add(hashText(response.signedText));
  button.classList.add('encypher-sign-btn--signed');
  updateButtonPresentation(button, {
    ready: true,
    signed: true,
    surface: getEditorSurfaceKind(editor, editorType)
  });

  try {
    await navigator.clipboard.writeText(response.signedText);
  } catch (e) {
    void e;
  }

  activeEditors.get(editor.id)?.updateVisibility?.();
  return response;
}

/**
 * Attach sign button to an editor
 */
function attachSignButton(editor) {
  const editorType = detectEditorType(editor);
  if (!editorType) return;
  if (shouldSkipEditor(editor, editorType)) return;

  // Skip if already attached
  const editorId = editor.id || `editor-${Math.random().toString(36).substr(2, 9)}`;
  if (!editor.id) editor.id = editorId;

  if (activeEditors.has(editorId)) return;

  // Create button
  const button = createSignButton(editorId);
  document.body.appendChild(button);
  const repositionHandler = createRepositionScheduler(button, editor);
  const surface = getEditorSurfaceKind(editor, editorType);
  const prefersHostedPlacement = shouldPreferHostedPlacement(editor);
  const resizeObserver = typeof ResizeObserver !== 'undefined'
    ? new ResizeObserver(repositionHandler)
    : null;
  const cleanupObserver = new MutationObserver(() => {
    if (!editor.isConnected) {
      cleanup();
    }
  });
  let cleanedUp = false;
  const cleanup = () => {
    if (cleanedUp) return;
    cleanedUp = true;
    button.remove();
    activeEditors.delete(editorId);
    cleanupObserver.disconnect();
    resizeObserver?.disconnect();
    window.removeEventListener('scroll', repositionHandler);
    window.removeEventListener('resize', repositionHandler);
    editor.removeEventListener('input', repositionHandler);
    editor.removeEventListener('mouseenter', handleMouseEnter);
    editor.removeEventListener('focus', handleFocus);
    editor.removeEventListener('blur', handleBlur);
    editor.removeEventListener('input', handleHostedInput);
    editor.removeEventListener('input', scheduleStateUpdate);
    button.removeEventListener('mouseenter', handleMouseEnter);
    button.removeEventListener('focus', handleMouseEnter);
  };

  const hostedPlacementActive = prefersHostedPlacement && attachButtonToPreferredHost(button, editor);
  if (!hostedPlacementActive) {
    positionButton(button, editor);
  }

  // Track editor
  activeEditors.set(editorId, {
    editorId,
    element: editor,
    type: editorType,
    button: button,
    cleanup: cleanup,
    surface,
    prefersHostedPlacement,
    isOnlineEditor: editorType === 'google-docs' || editorType === 'ms-word-online',
    insideModal: Boolean(editor.closest?.('dialog, [role="dialog"], [aria-modal="true"]') || editor.getRootNode()?.host?.closest?.('dialog, [role="dialog"], [aria-modal="true"]')),
    updateVisibility: (opts) => updateEditorButtonState(activeEditors.get(editorId), opts)
  });

  // Clean up button when editor is removed from the DOM (e.g. modal closed)
  const editorParent = editor.getRootNode() === document
    ? document.body
    : editor.getRootNode();
  cleanupObserver.observe(editorParent, { childList: true, subtree: true });

  // Atomic embedding-run handling for delete/backspace and copy/cut
  _attachEmbeddingRunHandlers(editor, editorType);

  // Online editors (Google Docs, MS Word Online): always-visible fixed button
  const isOnlineEditor = editorType === 'google-docs' || editorType === 'ms-word-online';
  const handleMouseEnter = () => setPrimaryEditor(editorId);
  const handleFocus = () => {
    setPrimaryEditor(editorId);
    repositionHandler();
    activeEditors.get(editorId)?.updateVisibility?.({ forceVisible: true, expanded: true });
  };
  const handleBlur = () => {
    setTimeout(() => {
      if (!document.querySelector('.encypher-sign-ui')) {
        activeEditors.get(editorId)?.updateVisibility?.();
      }
    }, 200);
  };
  const handleHostedInput = () => {
    if (!attachButtonToPreferredHost(button, editor)) {
      repositionHandler();
    }
  };
  let inputTimer = null;
  const scheduleStateUpdate = () => {
    clearTimeout(inputTimer);
    inputTimer = setTimeout(() => {
      activeEditors.get(editorId)?.updateVisibility?.();
    }, EDITOR_CONFIG.debounceMs);
  };

  if (isOnlineEditor) {
    button.style.position = 'fixed';
    button.style.bottom = `${EDITOR_CONFIG.viewportMargin}px`;
    button.style.right = `${EDITOR_CONFIG.viewportMargin}px`;
    button.style.top = 'auto';
    button.style.left = 'auto';
    button.dataset.placement = 'floating';
    updateButtonPresentation(button, {
      ready: (getEditorText(editor, editorType) || '').trim().length >= EDITOR_CONFIG.minTextLength,
      signed: button.classList.contains('encypher-sign-btn--signed'),
      surface
    });
    button.classList.add('encypher-sign-btn--visible', 'encypher-sign-btn--expanded');
  } else {
    // Reposition on scroll/resize
    window.addEventListener('scroll', repositionHandler, { passive: true });
    window.addEventListener('resize', repositionHandler, { passive: true });
    editor.addEventListener('input', handleHostedInput);
    editor.addEventListener('input', scheduleStateUpdate);
    resizeObserver?.observe(editor);
    if (editor.parentElement) {
      resizeObserver?.observe(editor.parentElement);
    }

    // Show/hide based on focus
    editor.addEventListener('focus', handleFocus);
    editor.addEventListener('blur', handleBlur);
    editor.addEventListener('mouseenter', handleMouseEnter);
    button.addEventListener('mouseenter', handleMouseEnter);
    button.addEventListener('focus', handleMouseEnter);

    // Determine if editor is already active.  For shadow-DOM editors,
    // document.activeElement returns the shadow host, so also walk
    // through shadowRoot.activeElement chains.
    let active = document.activeElement;
    while (active && active.shadowRoot && active.shadowRoot.activeElement) {
      active = active.shadowRoot.activeElement;
    }
    const editorIsActive = (active === editor);

    // Also treat the editor as active when it lives inside a dialog /
    // modal overlay (the user clearly intends to type).
    const insideModal = Boolean(editor.closest?.('dialog, [role="dialog"], [aria-modal="true"]')
        || editor.getRootNode()?.host?.closest?.('dialog, [role="dialog"], [aria-modal="true"]'));

    // Show button immediately when the editor is focused OR inside an
    // open modal — users can dismiss it, but it should default to
    // visible so they discover the feature.
    if (editorIsActive || insideModal) {
      setPrimaryEditor(editorId);
      if (!attachButtonToPreferredHost(button, editor)) {
        repositionHandler();
      }
    }
    updateEditorButtonState(activeEditors.get(editorId), { expanded: isOnlineEditor });
  }

  // Check if content is already signed
  const text = getEditorText(editor, editorType);
  if (signedContentHashes.has(hashText(text))) {
    updateButtonPresentation(button, { ready: true, signed: true, surface });
  }

  button.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setPrimaryEditor(editorId);
    const hasModifier = e.shiftKey || e.altKey || e.metaKey || e.ctrlKey;
    const ready = (getEditorText(editor, editorType) || '').trim().length >= EDITOR_CONFIG.minTextLength;
    if (hasModifier || !ready || button.classList.contains('encypher-sign-btn--signed')) {
      showSigningUI(editor, editorType, button);
      return;
    }
    button.classList.add('encypher-sign-btn--busy');
    try {
      const result = await signEditorContent({
        editor,
        editorType,
        button,
        title: '',
        replaceContent: defaultAutoReplaceContent,
        manifestMode: defaultEmbeddingTechnique,
        segmentationLevel: defaultSegmentationLevel,
        documentType: defaultDocumentType,
      });
      if (result?.verificationUrl || result?.documentId) {
        showSigningUI(editor, editorType, button);
      } else {
        showNotification('success', `Signed as ${getSignerLabel(cachedAccountInfo)}`);
      }
    } catch (error) {
      showNotification('error', error.message || 'Signing error');
    } finally {
      button.classList.remove('encypher-sign-btn--busy');
      activeEditors.get(editorId)?.updateVisibility?.();
    }
  });
}

/**
 * Scan page for editors
 */
function scanForEditorsInRoot(root) {
  if (!root?.querySelectorAll) return;

  const candidates = new Set();

  // Contenteditable elements
  const editables = root.querySelectorAll('[contenteditable="true"]');
  editables.forEach((el) => candidates.add(el));

  // Textareas (skip very small ones like search boxes)
  const textareas = root.querySelectorAll('textarea');
  textareas.forEach(ta => {
    if (ta.rows >= 3 || ta.offsetHeight >= 80) {
      candidates.add(ta);
    }
  });

  // Known editor classes
  const editorSelectors = [
    '.mce-content-body',
    '.ck-editor__editable',
    '.cke_editable',
    '.ql-editor',
    '.ProseMirror',
    '.tiptap',
    '.DraftEditor-root',
    '.public-DraftEditor-content',
    '.medium-editor-element',
    '.fr-element',
    '.note-editable'
  ];

  editorSelectors.forEach(selector => {
    const editors = root.querySelectorAll(selector);
    editors.forEach((el) => candidates.add(el));
  });

  Array.from(candidates).forEach(attachSignButton);
}

function scanForEditors() {
  const platform = detectOnlinePlatform();
  if (platform) {
    const onlineEditor = getOnlineEditorElement(platform);
    if (onlineEditor?.element) {
      attachSignButton(onlineEditor.element);
    }
  }

  scanForEditorsInRoot(document);
  scanShadowRootsForEditors(document);
}

function scanShadowRootsForEditors(root = document) {
  if (!root?.querySelectorAll) return;

  const elements = root.querySelectorAll('*');
  elements.forEach((el) => {
    if (el.shadowRoot) {
      scanForEditorsInRoot(el.shadowRoot);
      scanShadowRootsForEditors(el.shadowRoot);
    }
  });
}

function observeForEditors() {
  if (editorObserverStarted || !document.body) return;
  editorObserverStarted = true;
  // Main document observer
  const observer = new MutationObserver(_handleMutations);
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Also observe any shadow roots that already exist
  document.querySelectorAll('*').forEach((el) => {
    if (el.shadowRoot) {
      scanForEditorsInRoot(el.shadowRoot);
      scanShadowRootsForEditors(el.shadowRoot);
    }
  });
}

function _handleMutations(mutations) {
  let shouldScan = false;

  for (const mutation of mutations) {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          if (node.shadowRoot) {
            scanForEditorsInRoot(node.shadowRoot);
            _observeShadowRoot(node.shadowRoot);
            shouldScan = true;
          }

          // Check if it's an editor or contains editors
          if (detectEditorType(node) ||
              node.querySelector?.('[contenteditable="true"], textarea')) {
            shouldScan = true;
            break;
          }
        }
      }
    }
    if (shouldScan) break;
  }

  if (shouldScan) {
    _scheduleScan();
  }
}

function _observeShadowRoot(shadowRoot) {
  if (!shadowRoot || _observedShadowRoots.has(shadowRoot)) return;
  _observedShadowRoots.add(shadowRoot);

  // Scan existing content inside the shadow root
  scanForEditorsInRoot(shadowRoot);
  scanShadowRootsForEditors(shadowRoot);

  // Watch for future mutations inside this shadow root
  const shadowObserver = new MutationObserver(_handleMutations);
  shadowObserver.observe(shadowRoot, {
    childList: true,
    subtree: true
  });
}

function _scheduleScan() {
  clearTimeout(observeForEditors.timeout);
  observeForEditors.timeout = setTimeout(scanForEditors, 500);
}

function getSiteKind() {
  const hostname = window.location.hostname;
  if (hostname === 'mail.google.com' || hostname === 'outlook.office.com' || hostname === 'outlook.live.com') {
    return 'email';
  }
  if (
    hostname === 'chat.openai.com' ||
    hostname === 'chatgpt.com' ||
    hostname === 'claude.ai' ||
    hostname === 'app.slack.com' ||
    hostname === 'discord.com'
  ) {
    return 'chat';
  }
  if (hostname === 'docs.google.com' || hostname === 'word.live.com' || hostname.endsWith('.officeapps.live.com')) {
    return 'document';
  }
  return 'generic';
}

function isElementVisible(element) {
  if (!element || !element.isConnected) return false;
  const style = window.getComputedStyle(element);
  if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
  const rect = element.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
}

function shouldSkipEditor(element, editorType) {
  if (!element || !editorType || !isElementVisible(element)) return true;
  if (element.matches?.('[disabled], [readonly], [aria-hidden="true"]')) return true;
  if (editorType === 'contenteditable') {
    const parentEditable = element.parentElement?.closest?.('[contenteditable="true"]');
    if (parentEditable && parentEditable !== element) return true;
  }
  if (editorType === 'input' && !['text', 'search', ''].includes(element.type || '')) return true;
  const rect = element.getBoundingClientRect();
  if (rect.width < 180 || rect.height < 28) return true;
  return false;
}

function getEditorSurfaceKind(editor, editorType) {
  if (editorType === 'google-docs' || editorType === 'ms-word-online') return 'document';
  const siteKind = getSiteKind();
  if (siteKind !== 'generic') return siteKind;
  if (editor.closest?.('[role="toolbar"], .ql-toolbar, .tox-toolbar, .ck-toolbar')) return 'document';
  return 'generic';
}

function getShortcutHint() {
  return 'Alt+Shift+S';
}

function getSignerLabel(accountInfo) {
  const info = accountInfo?.data || accountInfo || {};
  const publisherDisplayName = info?.publisherDisplayName;
  const organizationName = info?.organizationName;
  const baseName = publisherDisplayName || organizationName || 'your organization';
  return info?.anonymousPublisher ? `${baseName} (anonymous publisher)` : baseName;
}

async function getCachedAccountInfo() {
  if (cachedAccountInfo) return cachedAccountInfo;
  if (accountInfoPromise) return accountInfoPromise;
  accountInfoPromise = (async () => {
    try {
      const { apiKey } = await chrome.storage.local.get({ apiKey: '' });
      if (!apiKey) return null;
      const response = await chrome.runtime.sendMessage({
        type: 'GET_ACCOUNT_INFO',
        apiKey
      });
      cachedAccountInfo = response?.success ? response.data : null;
      return cachedAccountInfo;
    } catch (e) {
      return null;
    } finally {
      accountInfoPromise = null;
    }
  })();
  return accountInfoPromise;
}

/**
 * Get the visible text (stripping embedding chars) from a string.
 */
function _stripEmbeddingChars(text) {
  let result = '';
  for (const char of text || '') {
    const cp = char.codePointAt(0);
    if (!_isEmbeddingChar(cp)) {
      result += char;
    }
  }
  return result;
}

/**
 * Convert a codepoint offset into a UTF-16 string offset.
 */
function _codepointOffsetToUtf16(text, codepointOffset) {
  if (codepointOffset <= 0) return 0;
  let utf16Offset = 0;
  let seen = 0;
  for (const char of text || '') {
    if (seen >= codepointOffset) break;
    utf16Offset += char.length;
    seen += 1;
  }
  return utf16Offset;
}

/**
 * Normalize embedding-plan operations into grouped insertion points.
 */
function _normalizeEmbeddingPlanOperations(embeddingPlan, visibleText) {
  if (!embeddingPlan || !Array.isArray(embeddingPlan.operations)) {
    return null;
  }

  const totalCodepoints = [...(visibleText || '')].length;
  const grouped = new Map();

  for (const op of embeddingPlan.operations) {
    if (!op || typeof op.marker !== 'string' || typeof op.insert_after_index !== 'number') {
      return null;
    }
    const idx = op.insert_after_index;
    if (!Number.isInteger(idx) || idx < -1 || idx >= totalCodepoints) {
      return null;
    }
    const insertionOffset = idx + 1;
    grouped.set(insertionOffset, `${grouped.get(insertionOffset) || ''}${op.marker}`);
  }

  return Array.from(grouped.entries())
    .map(([cpOffset, marker]) => ({ cpOffset, marker }))
    .sort((a, b) => b.cpOffset - a.cpOffset);
}

function _applyMarkersToText(text, normalizedOps) {
  let result = text || '';
  for (const op of normalizedOps || []) {
    const utf16Offset = _codepointOffsetToUtf16(result, op.cpOffset);
    result = result.slice(0, utf16Offset) + op.marker + result.slice(utf16Offset);
  }
  return result;
}

function applyEmbeddingPlanToSelectionInPlace() {
  return false;
}

function applyEmbeddingPlanToOnlineEditorInPlace() {
  return false;
}

/**
 * Apply embedding-plan markers directly into an editor element.
 */
function applyEmbeddingPlanToEditorInPlace(editor, editorType, embeddingPlan, visibleText) {
  if (!embeddingPlan || !Array.isArray(embeddingPlan.operations) || !visibleText) {
    return false;
  }

  const normalizedOps = _normalizeEmbeddingPlanOperations(embeddingPlan, visibleText);
  if (!normalizedOps) return false;

  if (editorType === 'google-docs' || editorType === 'ms-word-online') {
    return false;
  }

  if (editorType === 'textarea' || editorType === 'input') {
    const signedText = _applyMarkersToText(editor.value || '', normalizedOps);
    editor.value = signedText;
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    editor.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }

  const currentText = getEditorText(editor, editorType);
  const signedText = _applyMarkersToText(currentText || visibleText, normalizedOps);
  setEditorText(editor, editorType, signedText);
  return true;
}

async function handleSignSelection(text) {
  const selectedText = String(text || '').trim();
  if (selectedText.length < EDITOR_CONFIG.minTextLength) {
    showNotification('error', 'Select text first (minimum 10 characters)');
    return;
  }

  try {
    const response = await chrome.runtime.sendMessage({
      type: 'SIGN_CONTENT',
      text: selectedText,
      options: {
        manifestMode: defaultEmbeddingTechnique,
        segmentationLevel: defaultSegmentationLevel,
        documentType: defaultDocumentType,
      }
    });

    if (!response?.success) {
      throw new Error(response?.error || 'Signing failed');
    }

    try {
      await navigator.clipboard.writeText(response.signedText);
    } catch (e) {
      void e;
    }

    showNotification('success', `Signed selection as ${getSignerLabel(cachedAccountInfo)}`);
  } catch (error) {
    showNotification('error', error.message || 'Signing error');
  }
}

function handleSmartBackspace(e) {
  const target = e.target;
  if (!target) return;

  const isEditable = target.tagName === 'TEXTAREA' || target.tagName === 'INPUT' || target.isContentEditable;
  if (!isEditable || e.key !== 'Backspace') return;

  if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
    const text = target.value || '';
    const selectionStart = target.selectionStart;
    const selectionEnd = target.selectionEnd;
    if (selectionStart == null || selectionEnd == null || selectionStart !== selectionEnd || selectionStart === 0) return;
    const chars = [...text];
    const cpOffset = [...text.slice(0, selectionStart)].length;
    const checkIdx = cpOffset - 1;
    if (checkIdx < 0 || !_isEmbeddingChar(chars[checkIdx]?.codePointAt(0))) return;
    const run = findEmbeddingRun(text, cpOffset);
    if (!run) return;
    e.preventDefault();
    const nextText = chars.slice(0, run.start).join('') + chars.slice(run.end).join('');
    target.value = nextText;
    const utf16 = _codepointOffsetToUtf16(nextText, run.start);
    target.setSelectionRange(utf16, utf16);
    target.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

/**
 * Attach smart backspace listeners to the document.
 */
function initSmartBackspace() {
  document.addEventListener('keydown', handleSmartBackspace, true);
}

function handleSignShortcut(e) {
  const shortcutPressed = e.altKey && e.shiftKey && String(e.key).toLowerCase() === 's';
  if (!shortcutPressed) return;

  e.preventDefault();
  const sel = window.getSelection();
  const text = sel?.toString();
  if (text && text.trim().length >= EDITOR_CONFIG.minTextLength) {
    handleSignSelection(text);
    return;
  }

  const editorInfo = Array.from(activeEditors.values()).find((info) => info.editorId === primaryEditorId)
    || Array.from(activeEditors.values()).find((info) => info.element === document.activeElement || info.element.contains?.(document.activeElement));

  if (editorInfo?.button) {
    editorInfo.button.click();
    return;
  }

  showNotification('error', 'Select text first (minimum 10 characters)');
}

function initSignShortcut() {
  document.addEventListener('keydown', handleSignShortcut);
}

// Listen for messages from service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'SIGN_SELECTION') {
    handleSignSelection(message.text);
    sendResponse({ received: true });
  }

  if (message.type === 'SCAN_EDITORS') {
    scanForEditors();
    sendResponse({ count: activeEditors.size });
  }
});

// Load settings and initialize
async function _initEditorSigner() {
  try {
    const settings = await chrome.storage.sync.get({
      showEditorButtons: true,
      defaultEmbeddingTechnique: 'micro',
      defaultSegmentationLevel: 'sentence',
      defaultDocumentType: 'article',
      autoReplaceContent: true,
    });
    editorButtonsEnabled = settings.showEditorButtons;
    defaultEmbeddingTechnique = normalizeEmbeddingTechnique(settings.defaultEmbeddingTechnique);
    defaultSegmentationLevel = settings.defaultSegmentationLevel;
    defaultDocumentType = settings.defaultDocumentType || 'article';
    defaultAutoReplaceContent = settings.autoReplaceContent !== false;
  } catch (e) {
    void e;
  }

  getCachedAccountInfo().catch(() => null);

  if (editorButtonsEnabled) {
    scanForEditors();
    observeForEditors();
  }

  initSmartBackspace();
  initSignShortcut();
}

// Listen for settings changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== 'sync') return;
  if (changes.showEditorButtons) {
    editorButtonsEnabled = changes.showEditorButtons.newValue;
    if (!editorButtonsEnabled) {
      for (const [, info] of activeEditors) {
        info.cleanup?.();
      }
      activeEditors.clear();
    } else {
      scanForEditors();
      observeForEditors();
    }
  }
  if (changes.defaultEmbeddingTechnique) {
    defaultEmbeddingTechnique = normalizeEmbeddingTechnique(changes.defaultEmbeddingTechnique.newValue);
  }
  if (changes.defaultSegmentationLevel) {
    defaultSegmentationLevel = changes.defaultSegmentationLevel.newValue;
  }
  if (changes.defaultDocumentType) {
    defaultDocumentType = changes.defaultDocumentType.newValue || 'article';
  }
  if (changes.autoReplaceContent) {
    defaultAutoReplaceContent = changes.autoReplaceContent.newValue !== false;
  }
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _initEditorSigner);
} else {
  _initEditorSigner();
}

// Expose for testing (attached to window so module.exports can reach them)
window._encypherEditorSigner = {
  detectEditorType,
  detectOnlinePlatform,
  getOnlineEditorElement,
  getEditorText,
  setEditorText,
  hashText,
  findEmbeddingRun,
  extractRunBytes,
  _isVS,
  _isEmbeddingChar,
  _stripEmbeddingChars,
  applyEmbeddingPlanToSelectionInPlace,
  applyEmbeddingPlanToOnlineEditorInPlace,
  applyEmbeddingPlanToEditorInPlace,
  _normalizeEmbeddingPlanOperations,
  _codepointOffsetToUtf16,
  VS_RANGES,
  ZWNBSP
};

})(); // end IIFE

// Export for testing (Node/Jest)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = (typeof window !== 'undefined' && window._encypherEditorSigner) || {};
}
