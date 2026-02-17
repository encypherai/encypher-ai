/**
 * Encypher C2PA Editor Signer
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
  button.setAttribute('title', 'Sign with Encypher C2PA');
  
  button.innerHTML = `
    <svg class="encypher-sign-btn__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <path d="M9 12l2 2 4-4"/>
    </svg>
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
  ui.innerHTML = `
    <div class="encypher-sign-ui__header">
      <h3>Sign Content</h3>
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
        <span class="encypher-sign-ui__btn-loading" hidden>Signing...</span>
      </button>
    </div>
  `;
  
  // Position near button
  const buttonRect = button.getBoundingClientRect();
  ui.style.position = 'fixed';
  ui.style.top = `${buttonRect.bottom + 8}px`;
  ui.style.right = `${window.innerWidth - buttonRect.right}px`;
  
  document.body.appendChild(ui);
  
  // Event handlers
  ui.querySelector('.encypher-sign-ui__close').addEventListener('click', () => ui.remove());
  ui.querySelector('[data-action="cancel"]').addEventListener('click', () => ui.remove());
  
  ui.querySelector('[data-action="sign"]').addEventListener('click', async (e) => {
    const signBtn = e.currentTarget;
    const btnText = signBtn.querySelector('.encypher-sign-ui__btn-text');
    const btnLoading = signBtn.querySelector('.encypher-sign-ui__btn-loading');
    const title = ui.querySelector('#encypher-sign-title').value.trim();
    const replaceContent = ui.querySelector('#encypher-replace-content').checked;
    
    // Show loading state
    btnText.hidden = true;
    btnLoading.hidden = false;
    signBtn.disabled = true;
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'SIGN_CONTENT',
        text: text,
        title: title || undefined
      });
      
      if (response && response.success) {
        if (replaceContent) {
          setEditorText(editor, editorType, response.signedText);
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
        btnLoading.hidden = true;
        signBtn.disabled = false;
      }
    } catch (error) {
      showNotification('error', error.message || 'Signing error');
      btnText.hidden = false;
      btnLoading.hidden = true;
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
  
  // Button click handler
  button.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    showSigningUI(editor, editorType, button);
  });
  
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

    // Initially visible if focused
    if (document.activeElement === editor) {
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
 * Observe DOM for dynamically added editors
 */
function observeForEditors() {
  const observer = new MutationObserver((mutations) => {
    let shouldScan = false;
    
    for (const mutation of mutations) {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.shadowRoot) {
              scanForEditorsInRoot(node.shadowRoot);
              scanShadowRootsForEditors(node.shadowRoot);
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
      // Debounce
      clearTimeout(observeForEditors.timeout);
      observeForEditors.timeout = setTimeout(scanForEditors, 500);
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
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
    const response = await chrome.runtime.sendMessage({
      type: 'SIGN_CONTENT',
      text: cleanText,
      options: provenance.length > 0 ? { previousEmbeddings: provenance } : {}
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
    const settings = await chrome.storage.sync.get({ showEditorButtons: true });
    editorButtonsEnabled = settings.showEditorButtons;
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
  if (area === 'sync' && changes.showEditorButtons) {
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
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _initEditorSigner);
} else {
  _initEditorSigner();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
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
    _normalizeEmbeddingPlanOperations,
    _codepointOffsetToUtf16,
    VS_RANGES,
    ZWNBSP
  };
}
