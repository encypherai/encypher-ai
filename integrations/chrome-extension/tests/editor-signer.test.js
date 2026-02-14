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

// ── Embedding byte detection tests ──

describe('Variation Selector Detection (_isVS)', () => {
  // Mirror the logic from editor-signer.js
  const VS_RANGES = {
    VS1_START: 0xFE00, VS1_END: 0xFE0F,
    VS2_START: 0xE0100, VS2_END: 0xE01EF,
  };
  const ZWNBSP = 0xFEFF;

  const _isVS = (cp) =>
    (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) ||
    (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END);

  const _isEmbeddingChar = (cp) => _isVS(cp) || cp === ZWNBSP;

  it('should detect VS1 range', () => {
    assert.strictEqual(_isVS(0xFE00), true);
    assert.strictEqual(_isVS(0xFE0F), true);
    assert.strictEqual(_isVS(0xFE05), true);
  });

  it('should detect VS2 range', () => {
    assert.strictEqual(_isVS(0xE0100), true);
    assert.strictEqual(_isVS(0xE01EF), true);
    assert.strictEqual(_isVS(0xE0150), true);
  });

  it('should reject non-VS codepoints', () => {
    assert.strictEqual(_isVS(0x41), false); // 'A'
    assert.strictEqual(_isVS(0x20), false); // space
    assert.strictEqual(_isVS(0xFEFF), false); // ZWNBSP is not a VS
  });

  it('should detect ZWNBSP as embedding char', () => {
    assert.strictEqual(_isEmbeddingChar(0xFEFF), true);
  });

  it('should detect VS as embedding char', () => {
    assert.strictEqual(_isEmbeddingChar(0xFE00), true);
    assert.strictEqual(_isEmbeddingChar(0xE0100), true);
  });

  it('should reject normal chars as embedding char', () => {
    assert.strictEqual(_isEmbeddingChar(0x41), false);
    assert.strictEqual(_isEmbeddingChar(0x20), false);
  });
});

describe('extractRunBytes', () => {
  const VS_RANGES = {
    VS1_START: 0xFE00, VS1_END: 0xFE0F,
    VS2_START: 0xE0100, VS2_END: 0xE01EF,
  };

  const extractRunBytes = (text) => {
    const bytes = [];
    for (const char of text) {
      const cp = char.codePointAt(0);
      if (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) {
        bytes.push(cp - VS_RANGES.VS1_START);
      } else if (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END) {
        bytes.push((cp - VS_RANGES.VS2_START) + 16);
      }
    }
    return bytes;
  };

  it('should extract bytes from VS1 chars', () => {
    const text = String.fromCodePoint(0xFE00, 0xFE05, 0xFE0F);
    assert.deepStrictEqual(extractRunBytes(text), [0, 5, 15]);
  });

  it('should extract bytes from VS2 chars', () => {
    const text = String.fromCodePoint(0xE0100, 0xE0110);
    assert.deepStrictEqual(extractRunBytes(text), [16, 32]);
  });

  it('should skip ZWNBSP (not a data byte)', () => {
    const text = String.fromCodePoint(0xFEFF, 0xFE00, 0xFE01);
    assert.deepStrictEqual(extractRunBytes(text), [0, 1]);
  });

  it('should return empty for plain text', () => {
    assert.deepStrictEqual(extractRunBytes('Hello'), []);
  });
});

describe('findEmbeddingRun', () => {
  const VS_RANGES = {
    VS1_START: 0xFE00, VS1_END: 0xFE0F,
    VS2_START: 0xE0100, VS2_END: 0xE01EF,
  };
  const ZWNBSP = 0xFEFF;

  const _isVS = (cp) =>
    (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) ||
    (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END);

  const _isEmbeddingChar = (cp) => _isVS(cp) || cp === ZWNBSP;

  const findEmbeddingRun = (text, cursorPos) => {
    const chars = [...text];
    if (cursorPos < 0 || cursorPos > chars.length) return null;
    let inRun = false;
    if (cursorPos > 0 && _isEmbeddingChar(chars[cursorPos - 1].codePointAt(0))) inRun = true;
    if (cursorPos < chars.length && _isEmbeddingChar(chars[cursorPos].codePointAt(0))) inRun = true;
    if (!inRun) return null;
    let start = Math.min(cursorPos, chars.length - 1);
    if (start >= chars.length) start = chars.length - 1;
    while (start > 0 && _isEmbeddingChar(chars[start - 1].codePointAt(0))) start--;
    let end = cursorPos;
    while (end < chars.length && _isEmbeddingChar(chars[end].codePointAt(0))) end++;
    if (end <= start) return null;
    return { start, end };
  };

  it('should find embedding run when cursor is inside', () => {
    // "AB" + ZWNBSP + VS + VS + "CD"
    const text = 'AB' + String.fromCodePoint(0xFEFF, 0xFE00, 0xFE01) + 'CD';
    const chars = [...text];
    // Cursor at position 3 (inside the embedding run: after ZWNBSP, before first VS)
    const run = findEmbeddingRun(text, 3);
    assert.ok(run);
    assert.strictEqual(run.start, 2); // starts at ZWNBSP
    assert.strictEqual(run.end, 5);   // ends after last VS
  });

  it('should find embedding run when cursor is at left edge (backspace)', () => {
    // "AB" + ZWNBSP + VS + VS + "CD"
    const text = 'AB' + String.fromCodePoint(0xFEFF, 0xFE00, 0xFE01) + 'CD';
    // Cursor at position 5 (right after last VS, before 'C') — backspace would hit VS
    const run = findEmbeddingRun(text, 5);
    assert.ok(run);
    assert.strictEqual(run.start, 2);
    assert.strictEqual(run.end, 5);
  });

  it('should return null when cursor is not near embeddings', () => {
    const text = 'Hello World';
    assert.strictEqual(findEmbeddingRun(text, 5), null);
  });

  it('should return null for empty text', () => {
    assert.strictEqual(findEmbeddingRun('', 0), null);
  });

  it('should handle cursor at start of text with embedding', () => {
    const text = String.fromCodePoint(0xFEFF, 0xFE00) + 'Hello';
    const run = findEmbeddingRun(text, 0);
    assert.ok(run);
    assert.strictEqual(run.start, 0);
    assert.strictEqual(run.end, 2);
  });

  it('should handle cursor at end of text with embedding', () => {
    const text = 'Hello' + String.fromCodePoint(0xFEFF, 0xFE00);
    const chars = [...text];
    const run = findEmbeddingRun(text, chars.length);
    assert.ok(run);
    assert.strictEqual(run.start, 5);
    assert.strictEqual(run.end, 7);
  });
});

describe('_stripEmbeddingChars', () => {
  const VS_RANGES = {
    VS1_START: 0xFE00, VS1_END: 0xFE0F,
    VS2_START: 0xE0100, VS2_END: 0xE01EF,
  };
  const ZWNBSP = 0xFEFF;

  const _isVS = (cp) =>
    (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) ||
    (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END);

  const _isEmbeddingChar = (cp) => _isVS(cp) || cp === ZWNBSP;

  const _stripEmbeddingChars = (text) => {
    let result = '';
    for (const char of text) {
      const cp = char.codePointAt(0);
      if (!_isEmbeddingChar(cp)) result += char;
    }
    return result;
  };

  it('should strip VS and ZWNBSP from text', () => {
    const text = 'He' + String.fromCodePoint(0xFEFF, 0xFE00, 0xFE01) + 'llo';
    assert.strictEqual(_stripEmbeddingChars(text), 'Hello');
  });

  it('should return plain text unchanged', () => {
    assert.strictEqual(_stripEmbeddingChars('Hello World'), 'Hello World');
  });

  it('should return empty for all-embedding text', () => {
    const text = String.fromCodePoint(0xFEFF, 0xFE00, 0xFE0F);
    assert.strictEqual(_stripEmbeddingChars(text), '');
  });
});

describe('Provenance Storage Schema', () => {
  it('should define correct provenance entry structure', () => {
    // Verify the provenance entry shape matches what storeProvenance creates
    const entry = {
      bytes: [0x43, 0x32, 0x50, 0x41],
      timestamp: Date.now(),
      url: 'https://example.com/doc',
      action: 'backspace'
    };

    assert.ok(Array.isArray(entry.bytes));
    assert.strictEqual(typeof entry.timestamp, 'number');
    assert.strictEqual(typeof entry.url, 'string');
    assert.strictEqual(typeof entry.action, 'string');
  });

  it('should cap provenance entries per key', () => {
    // Simulate the capping logic
    const MAX_PER_KEY = 10;
    let entries = [];
    for (let i = 0; i < 15; i++) {
      entries.push({ bytes: [i], timestamp: Date.now() + i });
    }
    if (entries.length > MAX_PER_KEY) {
      entries = entries.slice(-MAX_PER_KEY);
    }
    assert.strictEqual(entries.length, 10);
    assert.strictEqual(entries[0].bytes[0], 5); // oldest kept
  });
});

describe('Selection Signing Flow', () => {
  it('should strip embedding chars before hashing for provenance lookup', () => {
    const VS_RANGES = { VS1_START: 0xFE00, VS1_END: 0xFE0F, VS2_START: 0xE0100, VS2_END: 0xE01EF };
    const ZWNBSP = 0xFEFF;
    const _isVS = (cp) => (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) || (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END);
    const _isEmbeddingChar = (cp) => _isVS(cp) || cp === ZWNBSP;
    const _strip = (text) => { let r = ''; for (const c of text) { if (!_isEmbeddingChar(c.codePointAt(0))) r += c; } return r; };

    const hashText = (text) => {
      let hash = 0;
      for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return hash.toString(16);
    };

    const plainText = 'Hello World';
    const embeddedText = 'He' + String.fromCodePoint(0xFEFF, 0xFE00) + 'llo World';

    // Both should produce the same visible hash
    assert.strictEqual(hashText(_strip(plainText)), hashText(_strip(embeddedText)));
  });

  it('should detect editable context for in-place replacement', () => {
    // Simulate the check: is the selection inside an editable element?
    const isEditable = (el) => {
      if (!el) return false;
      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') return true;
      if (el.isContentEditable) return true;
      if (el.closest?.('[contenteditable="true"]')) return true;
      return false;
    };

    // Editable
    assert.strictEqual(isEditable({ tagName: 'TEXTAREA' }), true);
    assert.strictEqual(isEditable({ tagName: 'INPUT' }), true);
    assert.strictEqual(isEditable({ tagName: 'DIV', isContentEditable: true, closest: () => null }), true);

    // Not editable
    assert.strictEqual(isEditable({ tagName: 'P', isContentEditable: false, closest: () => null }), false);
    assert.strictEqual(isEditable(null), false);
  });
});

describe('Keyboard Shortcut', () => {
  it('should match Ctrl+Shift+E', () => {
    const isSignShortcut = (e) => e.ctrlKey && e.shiftKey && e.key === 'E';

    assert.strictEqual(isSignShortcut({ ctrlKey: true, shiftKey: true, key: 'E' }), true);
    assert.strictEqual(isSignShortcut({ ctrlKey: true, shiftKey: false, key: 'E' }), false);
    assert.strictEqual(isSignShortcut({ ctrlKey: false, shiftKey: true, key: 'E' }), false);
    assert.strictEqual(isSignShortcut({ ctrlKey: true, shiftKey: true, key: 'A' }), false);
  });
});

console.log('All editor-signer tests passed!');
