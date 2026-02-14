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
  const classList = element.classList;
  const id = element.id || '';
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
    
    case 'quill':
      // Quill stores instance on parent
      const quillContainer = element.closest('.ql-container');
      if (quillContainer?.__quill) {
        return quillContainer.__quill.getText();
      }
      return element.innerText || element.textContent || '';
    
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
    
    case 'quill':
      const quillContainer = element.closest('.ql-container');
      if (quillContainer?.__quill) {
        quillContainer.__quill.setText(text);
        return;
      }
      element.innerText = text;
      break;
    
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
 * Create signing status indicator
 */
function createStatusIndicator() {
  const indicator = document.createElement('div');
  indicator.className = 'encypher-sign-status';
  indicator.setAttribute('role', 'status');
  indicator.setAttribute('aria-live', 'polite');
  return indicator;
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

  // Contenteditable elements
  const editables = document.querySelectorAll('[contenteditable="true"]');
  editables.forEach(attachSignButton);
  
  // Textareas (skip very small ones like search boxes)
  const textareas = document.querySelectorAll('textarea');
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
    const editors = document.querySelectorAll(selector);
    editors.forEach(attachSignButton);
  });
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
 * Handle context menu signing
 */
async function handleContextMenuSign(text) {
  if (!text || text.trim().length < EDITOR_CONFIG.minTextLength) {
    showNotification('error', 'Selected text is too short to sign');
    return;
  }
  
  showNotification('info', 'Signing selected text...');
  
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'SIGN_CONTENT',
      text: text.trim()
    });
    
    if (response && response.success) {
      // Copy signed text to clipboard
      await navigator.clipboard.writeText(response.signedText);
      showNotification('success', 'Signed text copied to clipboard!');
    } else {
      showNotification('error', response?.error || 'Signing failed');
    }
  } catch (error) {
    showNotification('error', error.message || 'Signing error');
  }
}

// Listen for messages from service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'SIGN_SELECTION') {
    handleContextMenuSign(message.text);
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
}

// Listen for settings changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'sync' && changes.showEditorButtons) {
    editorButtonsEnabled = changes.showEditorButtons.newValue;
    if (!editorButtonsEnabled) {
      // Remove all sign buttons
      for (const [id, info] of activeEditors) {
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
    hashText
  };
}
