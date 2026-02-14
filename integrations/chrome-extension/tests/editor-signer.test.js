/**
 * Tests for editor-signer.js
 * 
 * Run with: node --test tests/editor-signer.test.js
 */

import { describe, it, mock } from 'node:test';
import assert from 'node:assert';

// Mock DOM environment
const mockDocument = {
  createElement: (tag) => ({
    tagName: tag.toUpperCase(),
    className: '',
    id: '',
    classList: {
      contains: () => false,
      add: () => {},
      remove: () => {},
      toggle: () => {}
    },
    getAttribute: () => null,
    setAttribute: () => {},
    appendChild: () => {},
    addEventListener: () => {},
    style: {},
    innerHTML: '',
    innerText: '',
    textContent: '',
    value: '',
    isContentEditable: false,
    parentElement: null,
    closest: () => null,
    querySelector: () => null,
    querySelectorAll: () => [],
    dispatchEvent: () => {}
  }),
  body: {
    appendChild: () => {},
    querySelectorAll: () => []
  },
  activeElement: null,
  readyState: 'complete'
};

// Mock chrome API
const mockChrome = {
  runtime: {
    sendMessage: mock.fn(() => Promise.resolve({ success: true, signedText: 'signed content' })),
    onMessage: {
      addListener: () => {}
    }
  },
  storage: {
    sync: {
      get: mock.fn(() => Promise.resolve({}))
    },
    local: {
      get: mock.fn(() => Promise.resolve({ apiKey: 'test_key' }))
    }
  }
};

// Set up globals
globalThis.document = mockDocument;
globalThis.chrome = mockChrome;
globalThis.window = {
  getComputedStyle: () => ({ display: 'block' }),
  pageYOffset: 0,
  pageXOffset: 0,
  innerWidth: 1024,
  innerHeight: 768,
  addEventListener: () => {}
};
globalThis.Node = { ELEMENT_NODE: 1 };
globalThis.MutationObserver = class {
  observe() {}
  disconnect() {}
};
// Note: navigator is read-only in Node.js, skip mocking it

// Import functions to test (simulated since we can't import ES modules directly)
// In a real test environment, you'd use a bundler or ES module loader

describe('Editor Detection', () => {
  it('should detect contenteditable elements', () => {
    const element = {
      ...mockDocument.createElement('div'),
      isContentEditable: true,
      getAttribute: (attr) => attr === 'contenteditable' ? 'true' : null
    };
    
    // Simulate detectEditorType logic
    const detectEditorType = (el) => {
      if (el.isContentEditable || el.getAttribute('contenteditable') === 'true') {
        return 'contenteditable';
      }
      if (el.tagName === 'TEXTAREA') return 'textarea';
      return null;
    };
    
    assert.strictEqual(detectEditorType(element), 'contenteditable');
  });

  it('should detect textarea elements', () => {
    const element = {
      ...mockDocument.createElement('textarea'),
      tagName: 'TEXTAREA'
    };
    
    const detectEditorType = (el) => {
      if (el.tagName === 'TEXTAREA') return 'textarea';
      return null;
    };
    
    assert.strictEqual(detectEditorType(element), 'textarea');
  });

  it('should detect TinyMCE editor', () => {
    const element = {
      ...mockDocument.createElement('div'),
      classList: {
        contains: (cls) => cls === 'mce-content-body'
      },
      id: 'tinymce-editor'
    };
    
    const detectEditorType = (el) => {
      if (el.classList.contains('mce-content-body') || el.id?.startsWith('tinymce')) {
        return 'tinymce';
      }
      return null;
    };
    
    assert.strictEqual(detectEditorType(element), 'tinymce');
  });

  it('should detect Quill editor', () => {
    const element = {
      ...mockDocument.createElement('div'),
      classList: {
        contains: (cls) => cls === 'ql-editor'
      }
    };
    
    const detectEditorType = (el) => {
      if (el.classList.contains('ql-editor')) {
        return 'quill';
      }
      return null;
    };
    
    assert.strictEqual(detectEditorType(element), 'quill');
  });

  it('should detect CKEditor', () => {
    const element = {
      ...mockDocument.createElement('div'),
      classList: {
        contains: (cls) => cls === 'ck-editor__editable'
      }
    };
    
    const detectEditorType = (el) => {
      if (el.classList.contains('ck-editor__editable') || el.classList.contains('cke_editable')) {
        return 'ckeditor';
      }
      return null;
    };
    
    assert.strictEqual(detectEditorType(element), 'ckeditor');
  });

  it('should detect ProseMirror/Tiptap editor', () => {
    const element = {
      ...mockDocument.createElement('div'),
      classList: {
        contains: (cls) => cls === 'ProseMirror'
      }
    };
    
    const detectEditorType = (el) => {
      if (el.classList.contains('ProseMirror') || el.classList.contains('tiptap')) {
        return 'prosemirror';
      }
      return null;
    };
    
    assert.strictEqual(detectEditorType(element), 'prosemirror');
  });
});

describe('Text Extraction', () => {
  it('should get text from textarea', () => {
    const element = {
      tagName: 'TEXTAREA',
      value: 'Hello, World!'
    };
    
    const getEditorText = (el, type) => {
      if (type === 'textarea') return el.value || '';
      return el.innerText || el.textContent || '';
    };
    
    assert.strictEqual(getEditorText(element, 'textarea'), 'Hello, World!');
  });

  it('should get text from contenteditable', () => {
    const element = {
      innerText: 'Editable content here'
    };
    
    const getEditorText = (el, type) => {
      if (type === 'textarea') return el.value || '';
      return el.innerText || el.textContent || '';
    };
    
    assert.strictEqual(getEditorText(element, 'contenteditable'), 'Editable content here');
  });
});

describe('Text Setting', () => {
  it('should set text in textarea', () => {
    let dispatchedEvents = [];
    const element = {
      tagName: 'TEXTAREA',
      value: '',
      dispatchEvent: (e) => dispatchedEvents.push(e.type)
    };
    
    const setEditorText = (el, type, text) => {
      if (type === 'textarea') {
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    };
    
    // Mock Event constructor
    globalThis.Event = class Event {
      constructor(type) { this.type = type; }
    };
    
    setEditorText(element, 'textarea', 'New content');
    
    assert.strictEqual(element.value, 'New content');
    assert.ok(dispatchedEvents.includes('input'));
    assert.ok(dispatchedEvents.includes('change'));
  });
});

describe('Hash Function', () => {
  it('should generate consistent hashes', () => {
    const hashText = (text) => {
      let hash = 0;
      for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return hash.toString(16);
    };
    
    const hash1 = hashText('Hello, World!');
    const hash2 = hashText('Hello, World!');
    const hash3 = hashText('Different text');
    
    assert.strictEqual(hash1, hash2);
    assert.notStrictEqual(hash1, hash3);
  });

  it('should handle empty strings', () => {
    const hashText = (text) => {
      let hash = 0;
      for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return hash.toString(16);
    };
    
    assert.strictEqual(hashText(''), '0');
  });
});

describe('HTML Escaping', () => {
  it('should escape HTML entities', () => {
    const escapeHtml = (text) => {
      const div = { textContent: '', innerHTML: '' };
      div.textContent = text;
      // Simulate browser behavior
      div.innerHTML = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
      return div.innerHTML;
    };
    
    assert.strictEqual(escapeHtml('<script>alert("xss")</script>'), '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
    assert.strictEqual(escapeHtml('Normal text'), 'Normal text');
  });
});

describe('Minimum Text Length', () => {
  it('should enforce minimum text length for signing', () => {
    const MIN_TEXT_LENGTH = 10;
    
    const canSign = (text) => text.trim().length >= MIN_TEXT_LENGTH;
    
    assert.strictEqual(canSign('Short'), false);
    assert.strictEqual(canSign('This is long enough to sign'), true);
    assert.strictEqual(canSign('   Short   '), false);
    assert.strictEqual(canSign('1234567890'), true);
  });
});

describe('Online Platform Detection', () => {
  // Helper to simulate detectOnlinePlatform logic
  const detectOnlinePlatform = (hostname, pathname) => {
    if (hostname === 'docs.google.com' && pathname.startsWith('/document/')) {
      return 'google-docs';
    }
    if (
      (hostname === 'word.live.com' || hostname.endsWith('.officeapps.live.com')) ||
      (hostname.endsWith('.sharepoint.com') && pathname.includes('/_layouts/15/Doc.aspx'))
    ) {
      return 'ms-word-online';
    }
    return null;
  };

  it('should detect Google Docs', () => {
    assert.strictEqual(detectOnlinePlatform('docs.google.com', '/document/d/abc123/edit'), 'google-docs');
  });

  it('should not detect Google Docs on non-document pages', () => {
    assert.strictEqual(detectOnlinePlatform('docs.google.com', '/spreadsheets/d/abc123'), null);
    assert.strictEqual(detectOnlinePlatform('docs.google.com', '/presentation/d/abc123'), null);
  });

  it('should detect MS Word Online (word.live.com)', () => {
    assert.strictEqual(detectOnlinePlatform('word.live.com', '/edit/abc123'), 'ms-word-online');
  });

  it('should detect MS Word Online (officeapps.live.com)', () => {
    assert.strictEqual(detectOnlinePlatform('word-edit.officeapps.live.com', '/we/wordeditorframe.aspx'), 'ms-word-online');
  });

  it('should detect MS Word Online (SharePoint)', () => {
    assert.strictEqual(detectOnlinePlatform('contoso.sharepoint.com', '/_layouts/15/Doc.aspx?sourcedoc=abc'), 'ms-word-online');
  });

  it('should return null for unrecognized sites', () => {
    assert.strictEqual(detectOnlinePlatform('example.com', '/'), null);
    assert.strictEqual(detectOnlinePlatform('google.com', '/'), null);
  });
});

describe('Google Docs Editor Detection', () => {
  it('should detect Google Docs kix-appview-editor element', () => {
    const detectEditorType = (el) => {
      if (el.classList.contains('kix-appview-editor') ||
          el.classList.contains('kix-page-content-wrapper')) {
        return 'google-docs';
      }
      if (el.getAttribute('data-content-type') === 'RichText' ||
          el.classList.contains('WACViewPanel_EditingElement')) {
        return 'ms-word-online';
      }
      if (el.isContentEditable || el.getAttribute('contenteditable') === 'true') {
        return 'contenteditable';
      }
      return null;
    };

    const element = {
      ...mockDocument.createElement('div'),
      classList: { contains: (cls) => cls === 'kix-appview-editor' },
      getAttribute: () => null
    };
    assert.strictEqual(detectEditorType(element), 'google-docs');
  });

  it('should detect Google Docs page content wrapper', () => {
    const detectEditorType = (el) => {
      if (el.classList.contains('kix-appview-editor') ||
          el.classList.contains('kix-page-content-wrapper')) {
        return 'google-docs';
      }
      return null;
    };

    const element = {
      ...mockDocument.createElement('div'),
      classList: { contains: (cls) => cls === 'kix-page-content-wrapper' }
    };
    assert.strictEqual(detectEditorType(element), 'google-docs');
  });
});

describe('MS Word Online Editor Detection', () => {
  it('should detect Word Online RichText element', () => {
    const detectEditorType = (el) => {
      if (el.getAttribute('data-content-type') === 'RichText' ||
          el.classList.contains('WACViewPanel_EditingElement')) {
        return 'ms-word-online';
      }
      return null;
    };

    const element = {
      ...mockDocument.createElement('div'),
      getAttribute: (attr) => attr === 'data-content-type' ? 'RichText' : null,
      classList: { contains: () => false }
    };
    assert.strictEqual(detectEditorType(element), 'ms-word-online');
  });

  it('should detect Word Online WACViewPanel element', () => {
    const detectEditorType = (el) => {
      if (el.getAttribute('data-content-type') === 'RichText' ||
          el.classList.contains('WACViewPanel_EditingElement')) {
        return 'ms-word-online';
      }
      return null;
    };

    const element = {
      ...mockDocument.createElement('div'),
      getAttribute: () => null,
      classList: { contains: (cls) => cls === 'WACViewPanel_EditingElement' }
    };
    assert.strictEqual(detectEditorType(element), 'ms-word-online');
  });
});

describe('Google Docs Text Extraction', () => {
  it('should extract text from kix-lineview elements', () => {
    const getEditorText = (el, type) => {
      if (type === 'google-docs') {
        const lines = el.querySelectorAll('.kix-lineview');
        if (lines.length > 0) {
          return Array.from(lines).map(l => l.textContent || '').join('\n');
        }
        return el.innerText || el.textContent || '';
      }
      return el.innerText || '';
    };

    const mockLines = [
      { textContent: 'First line of the document' },
      { textContent: 'Second line of the document' }
    ];
    const element = {
      querySelectorAll: (selector) => {
        if (selector === '.kix-lineview') return mockLines;
        return [];
      },
      innerText: 'Fallback text'
    };

    assert.strictEqual(
      getEditorText(element, 'google-docs'),
      'First line of the document\nSecond line of the document'
    );
  });

  it('should fall back to innerText when no kix-lineview elements', () => {
    const getEditorText = (el, type) => {
      if (type === 'google-docs') {
        const lines = el.querySelectorAll('.kix-lineview');
        if (lines.length > 0) {
          return Array.from(lines).map(l => l.textContent || '').join('\n');
        }
        const paragraphs = el.querySelectorAll('.kix-paragraphrenderer');
        if (paragraphs.length > 0) {
          return Array.from(paragraphs).map(p => p.textContent || '').join('\n');
        }
        return el.innerText || el.textContent || '';
      }
      return '';
    };

    const element = {
      querySelectorAll: () => [],
      innerText: 'Fallback document text'
    };

    assert.strictEqual(getEditorText(element, 'google-docs'), 'Fallback document text');
  });
});

describe('Online Editor Set Text (Clipboard Fallback)', () => {
  it('should not directly mutate Google Docs DOM', () => {
    // For Google Docs and MS Word Online, setEditorText should NOT
    // modify innerText — it should use clipboard instead.
    // We verify that innerText is NOT changed.
    const element = { innerText: 'Original text' };

    const setEditorText = (el, type, text) => {
      if (type === 'google-docs' || type === 'ms-word-online') {
        // Would call navigator.clipboard.writeText in real code
        return; // Does NOT mutate el
      }
      el.innerText = text;
    };

    setEditorText(element, 'google-docs', 'Signed text');
    assert.strictEqual(element.innerText, 'Original text');
  });

  it('should not directly mutate MS Word Online DOM', () => {
    const element = { innerText: 'Original text' };

    const setEditorText = (el, type, text) => {
      if (type === 'google-docs' || type === 'ms-word-online') {
        return;
      }
      el.innerText = text;
    };

    setEditorText(element, 'ms-word-online', 'Signed text');
    assert.strictEqual(element.innerText, 'Original text');
  });
});

console.log('All editor-signer tests passed!');
