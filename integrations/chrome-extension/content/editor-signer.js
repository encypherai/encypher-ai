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
  buttonOffset: { top: -40, right: 8 },
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
  button.className = 'encypher-sign-btn';
  button.id = `encypher-sign-${editorId}`;
  button.setAttribute('type', 'button');
  button.setAttribute('aria-label', 'Sign content with Encypher');
  button.setAttribute('title', 'Sign with Encypher');
  
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

/**
 * Position the sign button relative to editor
 */
function positionButton(button, editor) {
  const rect = editor.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
  
  button.style.position = 'absolute';
  button.style.top = `${rect.top + scrollTop + EDITOR_CONFIG.buttonOffset.top}px`;
  button.style.left = `${rect.right + scrollLeft - button.offsetWidth - EDITOR_CONFIG.buttonOffset.right}px`;
  button.style.zIndex = '10001';
}

/**
 * Show signing modal/dropdown
 */
function showSigningUI(editor, editorType, button) {
  // Remove any existing UI
  const existingUI = document.querySelector('.encypher-sign-ui');
  if (existingUI) existingUI.remove();
  
  const text = getEditorText(editor, editorType);
  if (text.trim().length < EDITOR_CONFIG.minTextLength) {
    showNotification('error', 'Content too short to sign (minimum 10 characters)');
    return;
  }
  
  const ui = document.createElement('div');
  ui.className = 'encypher-sign-ui';
  const _headerLogoSvg = typeof globalThis?.ENCYPHER_LOGO_SVG === 'string'
    ? globalThis.ENCYPHER_LOGO_SVG
    : '';
  ui.innerHTML = `
    <div class="encypher-sign-ui__header">
      <div class="encypher-sign-ui__header-brand">
        ${_headerLogoSvg ? `<span class="encypher-sign-ui__header-logo" aria-hidden="true">${_headerLogoSvg}</span>` : ''}
        <h3>Sign Content</h3>
      </div>
      <button class="encypher-sign-ui__close" aria-label="Close">&times;</button>
    </div>
    <div class="encypher-sign-ui__body">
      <div class="encypher-sign-ui__preview">
        <label>Content Preview</label>
        <div class="encypher-sign-ui__text">${escapeHtml(text.substring(0, 200))}${text.length > 200 ? '...' : ''}</div>
        <div class="encypher-sign-ui__meta">${text.length} characters</div>
      </div>
      <div class="encypher-sign-ui__options">
        <label for="encypher-sign-title">Document Title (optional)</label>
        <input type="text" id="encypher-sign-title" placeholder="Enter title...">
      </div>
      <div class="encypher-sign-ui__select-group">
        <label for="encypher-embedding-technique">Embedding Mode</label>
        <select id="encypher-embedding-technique" class="encypher-sign-ui__select">
          <option value="micro">Standard (recommended)</option>
          <option value="micro_no_embed_c2pa">Compact (no embedded C2PA)</option>
        </select>
      </div>
      <div class="encypher-sign-ui__select-group">
        <label for="encypher-segmentation-level">Embedding Frequency</label>
        <select id="encypher-segmentation-level" class="encypher-sign-ui__select">
          <option value="document">Entire content</option>
          <option value="section">Per section</option>
          <option value="paragraph">Per paragraph</option>
          <option value="sentence">Per sentence</option>
          <option value="word">Per word (Enterprise)</option>
        </select>
      </div>
      <div class="encypher-sign-ui__options">
        <label>
          <input type="checkbox" id="encypher-replace-content" checked>
          Replace content with signed version
        </label>
      </div>
    </div>
    <div class="encypher-sign-ui__footer">
      <button class="encypher-sign-ui__btn encypher-sign-ui__btn--secondary" data-action="cancel">Cancel</button>
      <button class="encypher-sign-ui__btn encypher-sign-ui__btn--primary" data-action="sign">
        <span class="encypher-sign-ui__btn-text">Sign Content</span>
        <span class="encypher-sign-ui__btn-loading">Signing...</span>
      </button>
    </div>
  `;
  
  // Position near button
  const buttonRect = button.getBoundingClientRect();
  ui.style.position = 'fixed';
  ui.style.top = `${buttonRect.bottom + 8}px`;
  ui.style.right = `${window.innerWidth - buttonRect.right}px`;
  
  document.body.appendChild(ui);

  // Set dropdown defaults from settings
  const embTechSelect = ui.querySelector('#encypher-embedding-technique');
  const segLevelSelect = ui.querySelector('#encypher-segmentation-level');
  if (embTechSelect) embTechSelect.value = defaultEmbeddingTechnique;
  if (segLevelSelect) segLevelSelect.value = defaultSegmentationLevel;

  // Event handlers
  ui.querySelector('.encypher-sign-ui__close').addEventListener('click', () => ui.remove());
  ui.querySelector('[data-action="cancel"]').addEventListener('click', () => ui.remove());
  
  // Guard: ignore clicks that arrive in the same event-loop tick as the UI
  // creation (the mouseup from the floating button can land on this submit
  // button if they overlap).
  let signReady = false;
  requestAnimationFrame(() => { signReady = true; });

  ui.querySelector('[data-action="sign"]').addEventListener('click', async (e) => {
    if (!signReady) return;
    const signBtn = e.currentTarget;
    const btnText = signBtn.querySelector('.encypher-sign-ui__btn-text');
    const btnLoading = signBtn.querySelector('.encypher-sign-ui__btn-loading');
    const title = ui.querySelector('#encypher-sign-title').value.trim();
    const replaceContent = ui.querySelector('#encypher-replace-content').checked;
    const manifestMode = ui.querySelector('#encypher-embedding-technique')?.value || defaultEmbeddingTechnique;
    const segmentationLevel = ui.querySelector('#encypher-segmentation-level')?.value || defaultSegmentationLevel;

    // Show loading state
    btnText.hidden = true;
    btnLoading.classList.add('encypher-sign-ui__btn-loading--active');
    signBtn.disabled = true;

    try {
      const response = await chrome.runtime.sendMessage({
        type: 'SIGN_CONTENT',
        text: text,
        title: title || undefined,
        options: { manifestMode, segmentationLevel }
      });
      
      if (response && response.success) {
        if (replaceContent) {
          // Prefer in-place embedding plan insertion: it preserves the editor's
          // DOM structure, placeholder text, undo history and avoids triggering
          // character-count issues from full text replacement.
          const applied = response.embeddingPlan
            ? applyEmbeddingPlanToEditorInPlace(editor, editorType, response.embeddingPlan, text)
            : false;
          if (!applied) {
            setEditorText(editor, editorType, response.signedText);
          }
        }
        
        // Track as signed
        signedContentHashes.add(hashText(response.signedText));
        
        // Update button state
        button.classList.add('encypher-sign-btn--signed');
        button.querySelector('.encypher-sign-btn__text').innerHTML = 'Signed <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px"><polyline points="20 6 9 17 4 12"/></svg>';
        
        showNotification('success', 'Content signed successfully!');
        ui.remove();
        
        // Copy to clipboard as backup
        try {
          await navigator.clipboard.writeText(response.signedText);
        } catch (e) {
          // Clipboard access may be denied
        }
      } else {
        showNotification('error', response?.error || 'Signing failed');
        btnText.hidden = false;
        btnLoading.classList.remove('encypher-sign-ui__btn-loading--active');
        signBtn.disabled = false;
      }
    } catch (error) {
      showNotification('error', error.message || 'Signing error');
      btnText.hidden = false;
      btnLoading.classList.remove('encypher-sign-ui__btn-loading--active');
      signBtn.disabled = false;
    }
  });
  
  // Close on outside click
  setTimeout(() => {
    document.addEventListener('click', function closeUI(e) {
      if (!ui.contains(e.target) && !button.contains(e.target)) {
        ui.remove();
        document.removeEventListener('click', closeUI);
      }
    });
  }, 100);
}

/**
 * Escape HTML for safe display
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Show notification toast
 */
function showNotification(type, message) {
  const notification = document.createElement('div');
  notification.className = `encypher-notification encypher-notification--${type}`;
  notification.setAttribute('role', 'alert');
  
  const icons = {
    success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
  };
  
  notification.innerHTML = `
    <div class="encypher-notification__icon">${icons[type] || icons.info}</div>
    <div class="encypher-notification__content">${escapeHtml(message)}</div>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remove after 4 seconds
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

// ── Helpers for Selection in both main document and shadow roots ──

function _getSelection(editor) {
  const root = editor.getRootNode?.() || document;
  return root.getSelection ? root.getSelection() : window.getSelection();
}

/**
 * Get the caret's text-node context: the node, its text content as a
 * codepoint array, and the caret's codepoint offset within that node.
 * Returns null when the caret isn't inside a text node (or there's a range
 * selection instead of a collapsed caret).
 */
function _getTextNodeCaret(editor, editorType) {
  if (editorType === 'textarea' || editorType === 'input') {
    if (editor.selectionStart !== editor.selectionEnd) return null;
    const text = editor.value;
    const utf16 = editor.selectionStart;
    if (utf16 == null) return null;
    const cpOffset = [...text.slice(0, utf16)].length;
    return { node: null, text, chars: [...text], cpOffset };
  }

  const sel = _getSelection(editor);
  if (!sel || sel.rangeCount === 0 || !sel.isCollapsed) return null;
  const range = sel.getRangeAt(0);
  const node = range.startContainer;
  if (node.nodeType !== Node.TEXT_NODE) return null;
  if (!editor.contains(node)) return null;
  const text = node.textContent || '';
  const cpOffset = [...text.slice(0, range.startOffset)].length;
  return { node, text, chars: [...text], cpOffset };
}

/**
 * Place the caret at codepoint offset `cpOffset` inside `textNode`
 * (for contenteditable) or at the corresponding UTF-16 position in a textarea.
 */
function _setCaretInTextNode(editor, editorType, textNode, text, cpOffset) {
  const utf16 = _codepointOffsetToUtf16(text, cpOffset);

  if (editorType === 'textarea' || editorType === 'input') {
    editor.setSelectionRange(utf16, utf16);
    return;
  }

  const sel = _getSelection(editor);
  if (!sel) return;
  const r = document.createRange();
  r.setStart(textNode, utf16);
  r.collapse(true);
  sel.removeAllRanges();
  sel.addRange(r);
}

// ── Embedding-run aware keyboard & clipboard handlers ──

/**
 * Attach handlers that treat contiguous embedding-char runs as atomic:
 *   - Backspace / Delete removes the entire run in one keystroke
 *   - ArrowLeft / ArrowRight skips over the run
 *   - Mouse click / Ctrl+Arrow / Home / End: post-hoc cursor nudge
 *   - Copy / Cut extends a partial selection to include the full run
 */
function _attachEmbeddingRunHandlers(editor, editorType) {
  if (editorType === 'google-docs' || editorType === 'ms-word-online') return;

  editor.addEventListener('keydown', (e) => {
    const isDelete = e.key === 'Backspace' || e.key === 'Delete';
    const isArrow  = e.key === 'ArrowLeft'  || e.key === 'ArrowRight';
    if (!isDelete && !isArrow) return;

    // For modified arrow keys (Shift, Ctrl, etc.) handle via post-hoc nudge
    if (isArrow && (e.shiftKey || e.ctrlKey || e.metaKey || e.altKey)) return;
    // For modified delete keys let the browser handle normally (Ctrl+Backspace = delete word)
    if (isDelete && (e.ctrlKey || e.metaKey)) return;

    const caret = _getTextNodeCaret(editor, editorType);
    if (!caret) return;

    const { node, text, chars, cpOffset } = caret;

    if (isArrow) {
      _handleArrowOverRun(e, editor, editorType, node, text, chars, cpOffset);
    } else {
      _handleDeleteRun(e, editor, editorType, node, text, chars, cpOffset);
    }
  });

  // Post-hoc nudge: after mouse clicks, Ctrl+Arrow, Home, End, etc.
  // If the caret lands inside an embedding run, nudge it to the nearest edge.
  const scheduleNudge = () => requestAnimationFrame(() => _nudgeCaret(editor, editorType));
  editor.addEventListener('mouseup', scheduleNudge);
  editor.addEventListener('keyup', (e) => {
    // Only nudge for navigation keys that might land inside a run
    if (e.ctrlKey || e.metaKey || e.key === 'Home' || e.key === 'End' ||
        ((e.key === 'ArrowLeft' || e.key === 'ArrowRight') && e.shiftKey)) {
      scheduleNudge();
    }
  });

  editor.addEventListener('copy', _extendSelectionForEmbeddingRuns);
  editor.addEventListener('cut', _extendSelectionForEmbeddingRuns);
}

/**
 * Arrow key: skip over an adjacent embedding run.
 */
function _handleArrowOverRun(e, editor, editorType, textNode, text, chars, cpOffset) {
  const goingRight = e.key === 'ArrowRight';

  // Check the character we'd step into
  const checkIdx = goingRight ? cpOffset : cpOffset - 1;
  if (checkIdx < 0 || checkIdx >= chars.length) return;
  if (!_isEmbeddingChar(chars[checkIdx].codePointAt(0))) return;

  const run = findEmbeddingRun(text, cpOffset);
  if (!run) return;

  e.preventDefault();
  const target = goingRight ? run.end : run.start;
  _setCaretInTextNode(editor, editorType, textNode, text, target);
}

/**
 * Backspace / Delete: remove the entire adjacent embedding run from the
 * text node directly, preserving surrounding DOM structure.
 */
function _handleDeleteRun(e, editor, editorType, textNode, text, chars, cpOffset) {
  const isBackspace = e.key === 'Backspace';

  // Check the character that the keystroke would delete
  const checkIdx = isBackspace ? cpOffset - 1 : cpOffset;
  if (checkIdx < 0 || checkIdx >= chars.length) return;
  if (!_isEmbeddingChar(chars[checkIdx].codePointAt(0))) return;

  const run = findEmbeddingRun(text, cpOffset);
  if (!run) return;

  e.preventDefault();

  // Splice the run out of the text, keeping everything else intact
  const newChars = [...chars.slice(0, run.start), ...chars.slice(run.end)];
  const newText = newChars.join('');

  if (editorType === 'textarea' || editorType === 'input') {
    editor.value = newText;
    const utf16 = _codepointOffsetToUtf16(newText, run.start);
    editor.setSelectionRange(utf16, utf16);
    editor.dispatchEvent(new Event('input', { bubbles: true }));
  } else {
    // Modify only this text node — preserves <p>, <br>, undo, etc.
    textNode.textContent = newText;
    _setCaretInTextNode(editor, editorType, textNode, newText, run.start);
    editor.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

/**
 * Post-hoc nudge: if the caret is inside an embedding run (e.g. after a
 * mouse click or Ctrl+Arrow), move it to the nearest visible-text edge.
 */
function _nudgeCaret(editor, editorType) {
  const caret = _getTextNodeCaret(editor, editorType);
  if (!caret) return;

  const { node, text, chars, cpOffset } = caret;
  if (cpOffset >= chars.length) return;
  if (!_isEmbeddingChar(chars[cpOffset]?.codePointAt(0))) {
    // Also check the char before the cursor
    if (cpOffset === 0 || !_isEmbeddingChar(chars[cpOffset - 1]?.codePointAt(0))) return;
  }

  const run = findEmbeddingRun(text, cpOffset);
  if (!run) return;

  // Move to whichever edge is closer
  const distStart = cpOffset - run.start;
  const distEnd   = run.end - cpOffset;
  const target = distStart <= distEnd ? run.start : run.end;
  if (target === cpOffset) return;
  _setCaretInTextNode(editor, editorType, node, text, target);
}

/**
 * On copy/cut, if the selection partially overlaps an embedding run,
 * extend the clipboard data to include the full run so the signature
 * isn't split.
 */
function _extendSelectionForEmbeddingRuns(e) {
  const target = e.target;
  const root = target?.getRootNode?.() || document;
  const sel = root.getSelection ? root.getSelection() : window.getSelection();
  if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return;

  const range = sel.getRangeAt(0);
  const container = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
    ? range.commonAncestorContainer
    : range.commonAncestorContainer.parentElement;
  if (!container) return;

  const editable = container.closest?.('[contenteditable="true"]') || container;

  const fullText = editable.innerText || editable.textContent || '';
  const selectedText = sel.toString();
  if (!selectedText) return;

  const preRange = document.createRange();
  preRange.selectNodeContents(editable);
  preRange.setEnd(range.startContainer, range.startOffset);
  const preText = preRange.toString();
  const startCp = [...preText].length;
  const endCp = startCp + [...selectedText].length;
  const chars = [...fullText];

  let newStart = startCp;
  let newEnd = endCp;

  if (newStart > 0 && newStart < chars.length && _isEmbeddingChar(chars[newStart].codePointAt(0))) {
    const run = findEmbeddingRun(fullText, newStart);
    if (run) newStart = run.start;
  }
  if (newEnd > 0 && newEnd < chars.length && _isEmbeddingChar(chars[newEnd - 1]?.codePointAt(0))) {
    const run = findEmbeddingRun(fullText, newEnd);
    if (run) newEnd = run.end;
  }

  if (newStart === startCp && newEnd === endCp) return;

  const extendedText = chars.slice(newStart, newEnd).join('');
  e.clipboardData.setData('text/plain', extendedText);
  e.preventDefault();
}

/**
 * Attach sign button to an editor
 */
function attachSignButton(editor) {
  const editorType = detectEditorType(editor);
  if (!editorType) return;
  
  // Skip if already attached
  const editorId = editor.id || `editor-${Math.random().toString(36).substr(2, 9)}`;
  if (!editor.id) editor.id = editorId;
  
  if (activeEditors.has(editorId)) return;
  
  // Create button
  const button = createSignButton(editorId);
  document.body.appendChild(button);
  
  // Position button
  positionButton(button, editor);
  
  // Track editor
  activeEditors.set(editorId, {
    element: editor,
    type: editorType,
    button: button
  });

  // Clean up button when editor is removed from the DOM (e.g. modal closed)
  const cleanupObserver = new MutationObserver(() => {
    if (!editor.isConnected) {
      button.remove();
      activeEditors.delete(editorId);
      cleanupObserver.disconnect();
    }
  });
  const editorParent = editor.getRootNode() === document
    ? document.body
    : editor.getRootNode();
  cleanupObserver.observe(editorParent, { childList: true, subtree: true });

  // Button click handler
  button.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    showSigningUI(editor, editorType, button);
  });

  // Atomic embedding-run handling for delete/backspace and copy/cut
  _attachEmbeddingRunHandlers(editor, editorType);

  // Online editors (Google Docs, MS Word Online): always-visible fixed button
  const isOnlineEditor = editorType === 'google-docs' || editorType === 'ms-word-online';

  if (isOnlineEditor) {
    button.style.position = 'fixed';
    button.style.bottom = '24px';
    button.style.right = '24px';
    button.style.top = 'auto';
    button.style.left = 'auto';
    button.classList.add('encypher-sign-btn--visible');
  } else {
    // Reposition on scroll/resize
    const repositionHandler = () => positionButton(button, editor);
    window.addEventListener('scroll', repositionHandler, { passive: true });
    window.addEventListener('resize', repositionHandler, { passive: true });

    // Show/hide based on focus
    editor.addEventListener('focus', () => {
      button.classList.add('encypher-sign-btn--visible');
    });

    editor.addEventListener('blur', () => {
      // Delay to allow button click
      setTimeout(() => {
        if (!document.querySelector('.encypher-sign-ui')) {
          button.classList.remove('encypher-sign-btn--visible');
        }
      }, 200);
    });

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
    const insideModal = editor.closest?.('dialog, [role="dialog"], [aria-modal="true"]')
        || editor.getRootNode()?.host?.closest?.('dialog, [role="dialog"], [aria-modal="true"]');

    // Show button immediately when the editor is focused OR inside an
    // open modal — users can dismiss it, but it should default to
    // visible so they discover the feature.
    if (editorIsActive || insideModal) {
      button.classList.add('encypher-sign-btn--visible');
    }
  }
  
  // Check if content is already signed
  const text = getEditorText(editor, editorType);
  if (signedContentHashes.has(hashText(text))) {
    button.classList.add('encypher-sign-btn--signed');
    button.querySelector('.encypher-sign-btn__text').innerHTML = 'Signed <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px"><polyline points="20 6 9 17 4 12"/></svg>';
  }
}

/**
 * Scan page for editors
 */
function scanForEditorsInRoot(root) {
  if (!root?.querySelectorAll) return;

  // Contenteditable elements
  const editables = root.querySelectorAll('[contenteditable="true"]');
  editables.forEach(attachSignButton);
  
  // Textareas (skip very small ones like search boxes)
  const textareas = root.querySelectorAll('textarea');
  textareas.forEach(ta => {
    if (ta.rows >= 3 || ta.offsetHeight >= 80) {
      attachSignButton(ta);
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
    editors.forEach(attachSignButton);
  });
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

function scanForEditors() {
  if (!editorButtonsEnabled) return;

  // Check for online editor platforms first
  const platform = detectOnlinePlatform();
  if (platform) {
    const editorInfo = getOnlineEditorElement(platform);
    if (editorInfo) {
      attachSignButton(editorInfo.element);
    }
    // On Google Docs / Word Online, don't scan for generic editors
    // to avoid attaching buttons to unrelated contenteditable regions
    return;
  }

  scanForEditorsInRoot(document);
  scanShadowRootsForEditors(document);
}

/**
 * Observe DOM for dynamically added editors.
 *
 * In addition to watching the main document, we also observe inside open
 * shadow roots (e.g. LinkedIn's #interop-outlet) because a MutationObserver
 * on document.body does NOT see mutations inside shadow trees.
 */
const _observedShadowRoots = new WeakSet();

function _scheduleScan() {
  clearTimeout(observeForEditors.timeout);
  observeForEditors.timeout = setTimeout(scanForEditors, 500);
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

function observeForEditors() {
  // Main document observer
  const observer = new MutationObserver(_handleMutations);
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Also observe any shadow roots that already exist
  document.querySelectorAll('*').forEach((el) => {
    if (el.shadowRoot) {
      _observeShadowRoot(el.shadowRoot);
    }
  });
}

/**
 * Get the visible text (stripping embedding chars) from a string.
 */
function _stripEmbeddingChars(text) {
  let result = '';
  for (const char of text) {
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
  for (const char of text) {
    if (seen >= codepointOffset) break;
    utf16Offset += char.length;
    seen += 1;
  }
  return utf16Offset;
}

/**
 * Normalize embedding-plan operations into grouped insertion points.
 * Returns null when operations are malformed for the provided visible text.
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

/**
 * Collect selected text-node segments covered by a range.
 */
function _collectRangeTextSegments(range) {
  const segments = [];
  const SHOW_TEXT = window.NodeFilter?.SHOW_TEXT || 4;
  const commonRoot = range.commonAncestorContainer.nodeType === Node.TEXT_NODE
    ? range.commonAncestorContainer.parentNode || range.commonAncestorContainer
    : range.commonAncestorContainer;

  const walker = document.createTreeWalker(commonRoot, SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    try {
      if (!range.intersectsNode(node)) {
        node = walker.nextNode();
        continue;
      }
    } catch (e) {
      node = walker.nextNode();
      continue;
    }

    let startOffset = 0;
    let endOffset = (node.textContent || '').length;

    if (node === range.startContainer) {
      startOffset = range.startOffset;
    }
    if (node === range.endContainer) {
      endOffset = range.endOffset;
    }

    if (endOffset > startOffset) {
      const text = (node.textContent || '').slice(startOffset, endOffset);
      segments.push({
        node,
        startOffset,
        endOffset,
        text,
        codepointLength: [...text].length,
      });
    }

    node = walker.nextNode();
  }

  return segments;
}

/**
 * Collect all text-node segments inside an element.
 */
function _collectElementTextSegments(element) {
  if (!element) return [];
  const segments = [];
  const SHOW_TEXT = window.NodeFilter?.SHOW_TEXT || 4;
  const walker = document.createTreeWalker(element, SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    const text = node.textContent || '';
    if (text.length > 0) {
      segments.push({
        node,
        startOffset: 0,
        endOffset: text.length,
        text,
        codepointLength: [...text].length,
      });
    }
    node = walker.nextNode();
  }
  return segments;
}

/**
 * Find a single (unique) UTF-16 occurrence for needle within haystack.
 * Returns -1 when not found or when multiple matches exist.
 */
function _findSingleUtf16Occurrence(haystack, needle) {
  if (!needle) return -1;
  const first = haystack.indexOf(needle);
  if (first === -1) return -1;
  const second = haystack.indexOf(needle, first + 1);
  if (second !== -1) return -1;
  return first;
}

/**
 * Build a normalized whitespace view of text and a mapping back to original
 * codepoint offsets. Used to tolerate editor-specific NBSP/newline drift.
 */
function _buildNormalizedWhitespaceView(text) {
  const normalizedChars = [];
  const normalizedToOriginalCp = [];
  const sourceChars = [...(text || '')];

  let prevWasSpace = false;
  for (let i = 0; i < sourceChars.length; i += 1) {
    const ch = sourceChars[i];
    const isSpaceLike = ch === '\u00A0' || ch === '\n' || ch === '\r' || ch === '\t' || ch === ' ';
    const out = isSpaceLike ? ' ' : ch;

    if (out === ' ') {
      if (prevWasSpace) continue;
      prevWasSpace = true;
    } else {
      prevWasSpace = false;
    }

    normalizedChars.push(out);
    normalizedToOriginalCp.push(i);
  }

  return {
    text: normalizedChars.join(''),
    normalizedToOriginalCp,
  };
}

/**
 * Find a single (unique) normalized occurrence and map back to original
 * codepoint start offset. Returns null when no unique match exists.
 */
function _findSingleNormalizedOccurrence(haystack, needle) {
  const hayView = _buildNormalizedWhitespaceView(haystack);
  const needleView = _buildNormalizedWhitespaceView(needle);

  const hayChars = [...hayView.text];
  const needleChars = [...needleView.text];
  if (!needleChars.length) return null;
  if (needleChars.length > hayChars.length) return null;

  const matchStarts = [];
  for (let i = 0; i <= hayChars.length - needleChars.length; i += 1) {
    let ok = true;
    for (let j = 0; j < needleChars.length; j += 1) {
      if (hayChars[i + j] !== needleChars[j]) {
        ok = false;
        break;
      }
    }
    if (ok) {
      matchStarts.push(i);
      if (matchStarts.length > 1) return null;
    }
  }

  if (matchStarts.length !== 1) return null;

  const normalizedStartCp = matchStarts[0];
  return {
    startCodepoint: hayView.normalizedToOriginalCp[normalizedStartCp] ?? 0,
    lengthCodepoints: needleChars.length,
  };
}

/**
 * Map a global codepoint offset to a concrete node/UTF-16 offset insertion point.
 */
function _mapCodepointOffsetToNodePoint(segments, cpOffset) {
  if (!segments.length) return null;
  let consumed = 0;

  for (const segment of segments) {
    const nextConsumed = consumed + segment.codepointLength;
    if (cpOffset <= nextConsumed) {
      const localCpOffset = cpOffset - consumed;
      const localUtf16Offset = _codepointOffsetToUtf16(segment.text, localCpOffset);
      return {
        node: segment.node,
        offset: segment.startOffset + localUtf16Offset,
      };
    }
    consumed = nextConsumed;
  }

  const last = segments[segments.length - 1];
  return {
    node: last.node,
    offset: last.endOffset,
  };
}

/**
 * Apply embedding-plan markers in-place to the selected contenteditable text,
 * preserving surrounding DOM structure whenever possible.
 */
function applyEmbeddingPlanToSelectionInPlace(embeddingPlan, visibleText) {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) return false;

  const range = sel.getRangeAt(0);
  if (range.collapsed) return false;

  const normalizedOps = _normalizeEmbeddingPlanOperations(embeddingPlan, visibleText);
  if (!normalizedOps) return false;

  const segments = _collectRangeTextSegments(range);
  if (!segments.length) return false;

  const rangeVisibleText = segments.map(s => s.text).join('');
  if (rangeVisibleText !== visibleText) {
    return false;
  }

  for (const op of normalizedOps) {
    const point = _mapCodepointOffsetToNodePoint(segments, op.cpOffset);
    if (!point || !point.node) {
      return false;
    }

    const current = point.node.textContent || '';
    point.node.textContent = current.slice(0, point.offset) + op.marker + current.slice(point.offset);
  }

  const lastSegment = segments[segments.length - 1];
  const lastNodeText = lastSegment.node.textContent || '';
  const trailingMarkers = normalizedOps
    .filter(op => op.cpOffset >= [...visibleText].length)
    .reduce((sum, op) => sum + op.marker.length, 0);
  const caretOffset = Math.min(lastSegment.endOffset + trailingMarkers, lastNodeText.length);

  const newRange = document.createRange();
  newRange.setStart(lastSegment.node, caretOffset);
  newRange.collapse(true);
  sel.removeAllRanges();
  sel.addRange(newRange);

  const container = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
    ? range.commonAncestorContainer
    : range.commonAncestorContainer.parentElement;
  const editRoot = container?.closest?.('[contenteditable="true"]') || container;
  editRoot?.dispatchEvent(new Event('input', { bubbles: true }));

  return true;
}

/**
 * Apply embedding-plan markers within online-editor roots when browser selection
 * ranges are non-standard (Google Docs / Office Online edge surfaces).
 */
function applyEmbeddingPlanToOnlineEditorInPlace(embeddingPlan, visibleText, onlinePlatform) {
  if (onlinePlatform !== 'google-docs' && onlinePlatform !== 'ms-word-online') {
    return false;
  }

  const normalizedOps = _normalizeEmbeddingPlanOperations(embeddingPlan, visibleText);
  if (!normalizedOps) return false;

  const editorInfo = getOnlineEditorElement(onlinePlatform);
  const editorRoot = editorInfo?.element;
  if (!editorRoot) return false;

  const segments = _collectElementTextSegments(editorRoot);
  if (!segments.length) return false;

  const fullText = segments.map(segment => segment.text).join('');
  const normalizedMatch = _findSingleNormalizedOccurrence(fullText, visibleText);

  let startCpOffset;
  if (normalizedMatch) {
    startCpOffset = normalizedMatch.startCodepoint;
  } else {
    const matchUtf16 = _findSingleUtf16Occurrence(fullText, visibleText);
    if (matchUtf16 < 0) {
      return false;
    }
    startCpOffset = [...fullText.slice(0, matchUtf16)].length;
  }

  for (const op of normalizedOps) {
    const absoluteCpOffset = startCpOffset + op.cpOffset;
    const point = _mapCodepointOffsetToNodePoint(segments, absoluteCpOffset);
    if (!point || !point.node) {
      return false;
    }

    const current = point.node.textContent || '';
    point.node.textContent = current.slice(0, point.offset) + op.marker + current.slice(point.offset);
  }

  editorRoot.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}

/**
 * Apply embedding-plan markers directly into an editor element (contenteditable
 * or textarea) without replacing the entire text content. This preserves the
 * editor's DOM structure, placeholder text, undo history, and internal state.
 * Returns true on success, false if the plan could not be applied in-place.
 */
function applyEmbeddingPlanToEditorInPlace(editor, editorType, embeddingPlan, visibleText) {
  if (!embeddingPlan || !Array.isArray(embeddingPlan.operations) || !visibleText) {
    return false;
  }

  // Textarea / input: simple string splice
  if (editorType === 'textarea' || editorType === 'input') {
    const normalizedOps = _normalizeEmbeddingPlanOperations(embeddingPlan, visibleText);
    if (!normalizedOps) return false;

    const chars = [...editor.value];
    // Ops are sorted descending, so splice from end to preserve offsets
    for (const op of normalizedOps) {
      const utf16Offset = _codepointOffsetToUtf16(editor.value, op.cpOffset);
      editor.value = editor.value.slice(0, utf16Offset) + op.marker + editor.value.slice(utf16Offset);
    }
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    editor.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }

  // Online editors (Google Docs, MS Word Online): use dedicated function
  const onlinePlatform = detectOnlinePlatform();
  if (onlinePlatform === 'google-docs' || onlinePlatform === 'ms-word-online') {
    return applyEmbeddingPlanToOnlineEditorInPlace(embeddingPlan, visibleText, onlinePlatform);
  }

  // Contenteditable: walk text nodes and insert markers.
  // getEditorText() uses innerText which synthesises \n for block elements
  // (<p>, <br>, <div>) that don't exist in raw text nodes.  We must handle
  // the offset difference between innerText codepoints and DOM text-node
  // codepoints so the embedding plan lands in the right place.
  const normalizedOps = _normalizeEmbeddingPlanOperations(embeddingPlan, visibleText);
  if (!normalizedOps) return false;

  const segments = _collectElementTextSegments(editor);
  if (!segments.length) return false;

  const fullText = segments.map(s => s.text).join('');

  // Compare with whitespace stripped — innerText adds synthetic \n for block
  // elements that don't appear in raw text nodes.
  const normalize = (t) => t.replace(/[\s\u00A0]+/g, ' ').trim();
  const fullTextClean = normalize(_stripEmbeddingChars(fullText));
  const visibleTextClean = normalize(visibleText);
  if (fullTextClean !== visibleTextClean) {
    return false;
  }

  const totalSegmentCp = segments.reduce((sum, s) => sum + s.codepointLength, 0);

  for (const op of normalizedOps) {
    // Clamp cpOffset: visibleText may be longer than DOM text due to
    // synthetic newlines.  Offsets at/beyond the end of DOM text should map
    // to the very end of the last text node.
    const mappedCpOffset = Math.min(op.cpOffset, totalSegmentCp);
    const point = _mapCodepointOffsetToNodePoint(segments, mappedCpOffset);
    if (!point || !point.node) return false;

    const current = point.node.textContent || '';
    point.node.textContent = current.slice(0, point.offset) + op.marker + current.slice(point.offset);
  }

  editor.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}

/**
 * Try to replace the current selection in-place within an editable element.
 * Returns true if replacement succeeded, false if not in an editable context.
 */
function replaceSelectionInPlace(signedText) {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) return false;

  const range = sel.getRangeAt(0);
  const container = range.commonAncestorContainer;
  const editableEl = container.nodeType === Node.ELEMENT_NODE
    ? container
    : container.parentElement;

  if (!editableEl) return false;

  // Check if we're inside a textarea/input
  const active = document.activeElement;
  if (active && (active.tagName === 'TEXTAREA' || active.tagName === 'INPUT')) {
    const start = active.selectionStart;
    const end = active.selectionEnd;
    if (start !== undefined && end !== undefined) {
      active.value = active.value.slice(0, start) + signedText + active.value.slice(end);
      active.selectionStart = active.selectionEnd = start + signedText.length;
      active.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }
  }

  // Check if we're inside a contenteditable element
  if (editableEl.isContentEditable || editableEl.closest('[contenteditable="true"]')) {
    range.deleteContents();
    const textNode = document.createTextNode(signedText);
    range.insertNode(textNode);
    // Move cursor to end of inserted text
    sel.removeAllRanges();
    const newRange = document.createRange();
    newRange.setStartAfter(textNode);
    newRange.collapse(true);
    sel.addRange(newRange);
    // Trigger input event
    const editRoot = editableEl.closest('[contenteditable="true"]') || editableEl;
    editRoot.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }

  return false;
}

/**
 * Handle signing of selected text.
 * Replaces selection in-place when in an editable context, otherwise copies to clipboard.
 */
async function handleSignSelection(text) {
  if (!text || text.trim().length < EDITOR_CONFIG.minTextLength) {
    showNotification('error', 'Selected text is too short to sign');
    return;
  }

  const cleanText = text.trim();
  const visibleText = _stripEmbeddingChars(cleanText);
  const visibleHash = hashText(visibleText);

  showNotification('info', 'Signing selected text...');

  // Check for provenance (previous embeddings on this content)
  const provenance = await getProvenance(visibleHash);

  try {
    const signOptions = {
      manifestMode: defaultEmbeddingTechnique,
      segmentationLevel: defaultSegmentationLevel,
    };
    if (provenance.length > 0) {
      signOptions.previousEmbeddings = provenance;
    }
    const response = await chrome.runtime.sendMessage({
      type: 'SIGN_CONTENT',
      text: cleanText,
      options: signOptions
    });

    if (response && response.success) {
      // Store old embedding bytes as provenance before replacing
      const oldBytes = extractRunBytes(cleanText);
      if (oldBytes.length > 0) {
        await storeProvenance(visibleHash, oldBytes, { action: 'resign' });
      }

      // Try DOM-preserving embedding-plan insertion first when available
      let replaced = false;
      if (response.embeddingPlan) {
        replaced = applyEmbeddingPlanToSelectionInPlace(response.embeddingPlan, visibleText);

        const onlinePlatform = detectOnlinePlatform();
        if (!replaced && (onlinePlatform === 'google-docs' || onlinePlatform === 'ms-word-online')) {
          replaced = applyEmbeddingPlanToOnlineEditorInPlace(response.embeddingPlan, visibleText, onlinePlatform);
        }
      }

      // Fallback to full signed-text replacement
      if (!replaced) {
        replaced = replaceSelectionInPlace(response.signedText);
      }
      if (replaced) {
        signedContentHashes.add(hashText(response.signedText));
        showNotification('success', 'Content signed and replaced!');
      } else {
        // Fallback: copy to clipboard
        try {
          await navigator.clipboard.writeText(response.signedText);
          showNotification('success', 'Signed text copied to clipboard!');
        } catch (e) {
          showNotification('error', 'Could not copy to clipboard');
        }
      }
    } else {
      showNotification('error', response?.error || 'Signing failed');
    }
  } catch (error) {
    showNotification('error', error.message || 'Signing error');
  }
}

// ── Smart Backspace ──

/**
 * Handle keydown events in editable elements to detect backspace/delete
 * into embedding byte runs. When detected, auto-delete the entire run
 * and store the bytes as provenance.
 */
function handleSmartBackspace(e) {
  if (e.key !== 'Backspace' && e.key !== 'Delete') return;

  const target = e.target;
  let text, cursorPos;

  // Textarea / input
  if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
    text = target.value;
    cursorPos = target.selectionStart;
    if (target.selectionStart !== target.selectionEnd) return; // has selection, let default handle it
  } else if (target.isContentEditable || target.closest?.('[contenteditable="true"]')) {
    // Contenteditable: get text from the focused text node
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || !sel.isCollapsed) return;
    const node = sel.focusNode;
    if (!node || node.nodeType !== Node.TEXT_NODE) return;
    text = node.textContent || '';
    cursorPos = sel.focusOffset;
  } else {
    return;
  }

  // Adjust cursor for Delete key (acts like backspace at cursorPos+1)
  const effectivePos = e.key === 'Delete' ? cursorPos + 1 : cursorPos;

  const run = findEmbeddingRun(text, effectivePos);
  if (!run) return;

  // Found an embedding run — prevent default and delete the whole run
  e.preventDefault();

  // Extract bytes for provenance before deleting
  const chars = [...text];
  const runText = chars.slice(run.start, run.end).join('');
  const runBytes = extractRunBytes(runText);
  const visibleText = _stripEmbeddingChars(text);
  const visibleHash = hashText(visibleText);

  // Store provenance asynchronously
  if (runBytes.length > 0) {
    storeProvenance(visibleHash, runBytes, { action: 'backspace' });
  }

  // Delete the run
  if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
    // Convert char indices to string indices for textarea
    const prefix = chars.slice(0, run.start).join('');
    const suffix = chars.slice(run.end).join('');
    target.value = prefix + suffix;
    target.selectionStart = target.selectionEnd = prefix.length;
    target.dispatchEvent(new Event('input', { bubbles: true }));
  } else {
    // Contenteditable: replace the text node content
    const sel = window.getSelection();
    const node = sel.focusNode;
    const prefix = chars.slice(0, run.start).join('');
    const suffix = chars.slice(run.end).join('');
    node.textContent = prefix + suffix;
    // Restore cursor position
    const newRange = document.createRange();
    const newPos = Math.min(prefix.length, node.textContent.length);
    newRange.setStart(node, newPos);
    newRange.collapse(true);
    sel.removeAllRanges();
    sel.addRange(newRange);
    // Trigger input
    const editRoot = target.closest?.('[contenteditable="true"]') || target;
    editRoot.dispatchEvent(new Event('input', { bubbles: true }));
  }

  showNotification('info', 'Embedding removed');
}

/**
 * Attach smart backspace listeners to the document.
 * Uses capture phase to intercept before editor frameworks.
 */
function initSmartBackspace() {
  document.addEventListener('keydown', handleSmartBackspace, true);
}

// ── Keyboard shortcut: Ctrl+Shift+E to sign selection ──

function handleSignShortcut(e) {
  if (e.ctrlKey && e.shiftKey && e.key === 'E') {
    e.preventDefault();
    const sel = window.getSelection();
    const text = sel?.toString();
    if (text && text.trim().length >= EDITOR_CONFIG.minTextLength) {
      handleSignSelection(text);
    } else {
      showNotification('error', 'Select text first (minimum 10 characters)');
    }
  }
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
    });
    editorButtonsEnabled = settings.showEditorButtons;
    defaultEmbeddingTechnique = normalizeEmbeddingTechnique(settings.defaultEmbeddingTechnique);
    defaultSegmentationLevel = settings.defaultSegmentationLevel;
  } catch (e) {
    // Default to enabled if storage fails
  }
  if (editorButtonsEnabled) {
    scanForEditors();
    observeForEditors();
  }
  // Always init smart backspace and sign shortcut (independent of editor buttons)
  initSmartBackspace();
  initSignShortcut();
}

// Listen for settings changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== 'sync') return;
  if (changes.showEditorButtons) {
    editorButtonsEnabled = changes.showEditorButtons.newValue;
    if (!editorButtonsEnabled) {
      // Remove all sign buttons
      for (const [, info] of activeEditors) {
        info.button?.remove();
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
