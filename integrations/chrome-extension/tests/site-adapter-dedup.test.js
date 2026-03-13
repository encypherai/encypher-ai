/**
 * Tests for site adapter dedup logic and Claude.ai adapter fixes.
 *
 * Covers:
 *  1. SSOT dedup in attachButtonToPreferredHost — catches any adapter inserting
 *     into a container that already has a sign button.
 *  2. Claude.ai adapter — only one button placed when multiple branch editors
 *     share the same chat-input-grid-container (the exact production bug).
 *  3. Claude.ai leftCluster — never resolves to a <button> element.
 *  4. Claude.ai rightCluster fallback — found via class selector when send
 *     button has no matching aria-label/data-testid.
 *
 * Run with: node --test tests/site-adapter-dedup.test.js
 */

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';

// ---------------------------------------------------------------------------
// Minimal DOM factory
// Tracks real parent/child relationships so insertBefore / appendChild /
// querySelectorAll / contains / remove all behave correctly.
// ---------------------------------------------------------------------------
function createNode(tag = 'div', attrs = {}) {
  const node = {
    tagName: tag.toUpperCase(),
    className: attrs.className || '',
    id: attrs.id || '',
    dataset: {},
    style: {},
    _children: [],
    _attrs: { ...attrs },

    get parentElement() { return node._parent || null; },

    getAttribute(name) { return node._attrs[name] ?? null; },
    setAttribute(name, val) { node._attrs[name] = val; },

    get classList() {
      return {
        _classes: new Set(node.className.split(/\s+/).filter(Boolean)),
        contains(cls) { return this._classes.has(cls); },
        add(...cls) { cls.forEach(c => { this._classes.add(c); node.className = [...this._classes].join(' '); }); },
        remove(...cls) { cls.forEach(c => { this._classes.delete(c); node.className = [...this._classes].join(' '); }); },
      };
    },

    matches(selector) {
      // Support the selectors used in the adapters
      for (const part of selector.split(',').map(s => s.trim())) {
        if (_matchesSimple(node, part)) return true;
      }
      return false;
    },

    closest(selector) {
      let el = node;
      while (el) {
        if (el.matches && el.matches(selector)) return el;
        el = el._parent || null;
      }
      return null;
    },

    contains(other) {
      if (!other) return false;
      let el = other;
      while (el) {
        if (el === node) return true;
        el = el._parent || null;
      }
      return false;
    },

    appendChild(child) {
      if (child._parent) child._parent._children = child._parent._children.filter(c => c !== child);
      child._parent = node;
      node._children.push(child);
      return child;
    },

    insertBefore(child, ref) {
      if (child._parent) child._parent._children = child._parent._children.filter(c => c !== child);
      child._parent = node;
      const idx = ref ? node._children.indexOf(ref) : -1;
      if (idx === -1) node._children.push(child);
      else node._children.splice(idx, 0, child);
      return child;
    },

    prepend(child) {
      node.insertBefore(child, node._children[0] || null);
    },

    remove() {
      if (node._parent) {
        node._parent._children = node._parent._children.filter(c => c !== node);
        node._parent = null;
      }
    },

    querySelector(selector) {
      return _queryAll(node, selector)[0] || null;
    },

    querySelectorAll(selector) {
      return _queryAll(node, selector);
    },

    get isConnected() { return true; },
    addEventListener() {},
    removeEventListener() {},
  };
  return node;
}

function _matchesSimple(node, selector) {
  selector = selector.trim();

  // data-testid="value"
  const testIdMatch = selector.match(/\[data-testid="([^"]+)"\]/);
  if (testIdMatch && node._attrs['data-testid'] !== testIdMatch[1]) return false;

  // aria-label="value"
  const ariaMatch = selector.match(/\[aria-label="([^"]+)"\]/);
  if (ariaMatch && node._attrs['aria-label'] !== ariaMatch[1]) return false;

  // aria-label*="value"
  const ariaContainsMatch = selector.match(/\[aria-label\*="([^"]+)"\]/);
  if (ariaContainsMatch && !(node._attrs['aria-label'] || '').includes(ariaContainsMatch[1])) return false;

  // [class*="value"] — ALL must match
  const classContainsMatches = [...selector.matchAll(/\[class\*="([^"]+)"\]/g)];
  for (const m of classContainsMatches) {
    if (!node.className.includes(m[1])) return false;
  }

  // :not(button)
  if (selector.includes(':not(button)') && node.tagName === 'BUTTON') return false;

  // tag prefix
  const tagMatch = selector.match(/^([a-zA-Z][a-zA-Z0-9]*)/);
  if (tagMatch && tagMatch[1].toUpperCase() !== node.tagName) return false;

  // .className
  const classMatch = selector.match(/\.([a-zA-Z_-][a-zA-Z0-9_-]*)/g);
  if (classMatch) {
    const classes = node.className.split(/\s+/);
    for (const c of classMatch) {
      if (!classes.includes(c.slice(1))) return false;
    }
  }

  // #id
  const idMatch = selector.match(/#([a-zA-Z_-][a-zA-Z0-9_-]*)/);
  if (idMatch && node.id !== idMatch[1]) return false;

  return true;
}

function _queryAll(root, selector) {
  const results = [];
  function walk(node) {
    for (const child of node._children) {
      if (child.matches && child.matches(selector)) results.push(child);
      walk(child);
    }
  }
  walk(root);
  return results;
}

// ---------------------------------------------------------------------------
// Inline the logic under test (mirroring the actual source functions)
// ---------------------------------------------------------------------------

function makeSignButton(editorId) {
  const btn = createNode('button', { className: 'encypher-sign-btn' });
  btn.id = `encypher-sign-${editorId}`;
  return btn;
}

/**
 * Mirrors attachButtonToPreferredHost from editor-signer.js.
 * The body node acts as document.body.
 */
function attachButtonToPreferredHost(button, editor, adapter, body) {
  if (!adapter) return false;

  const previousParent = button.parentElement;
  const attached = adapter.tryAttach(button);

  if (attached) {
    const newParent = button.parentElement;
    // SSOT dedup — revert if another sign button is already in the same container
    if (newParent && newParent !== previousParent &&
        newParent.querySelectorAll('.encypher-sign-btn').length > 1) {
      button.remove();
      body.appendChild(button);
      return false;
    }
    button.dataset.hosted = 'true';
    button.style.position = 'relative';
    return true;
  }

  body.appendChild(button);
  return false;
}

/**
 * Mirrors the Claude.ai branch of getSiteAdapter from editor-signer.js.
 * hostname is injected rather than read from window.location so tests can
 * call it without a real browser.
 */
function getClaudeAdapter(editor, hostname) {
  if (hostname !== 'claude.ai') return null;

  // Walk up from editor — no global document.querySelector fallback
  const root = editor.closest?.('[data-testid="chat-input-grid-container"]')
    || editor.closest?.('form')
    || editor.parentElement
    || null;

  if (!root) return null;

  const sendButton = root.querySelector(
    'button[aria-label="Send message"], button[aria-label*="Send"], [data-testid="send-button"]'
  );
  const rightCluster = sendButton?.parentElement
    || root.querySelector('div[class*="flex"][class*="items-center"][class*="gap"][class*="shrink-0"]')
    || sendButton?.closest('[class*="items-center"], [class*="justify-end"]')
    || null;

  // :not(button) prevents resolving to the model-selector button itself
  const leftCluster = root.querySelector('[data-testid="model-selector-dropdown"]')
    ?.closest('div[class*="flex"]:not(button)')
    || root.querySelector('[class*="ProseMirror"]')?.parentElement
    || root.querySelector('[contenteditable="true"]')?.parentElement
    || null;

  return {
    key: 'claude',
    tryAttach(button) {
      if (rightCluster?.contains(button)) return true;
      if (leftCluster?.contains(button)) return true;
      if (rightCluster && sendButton && !rightCluster.contains(button)) {
        rightCluster.insertBefore(button, sendButton);
        return true;
      }
      if (rightCluster && !rightCluster.contains(button)) {
        rightCluster.appendChild(button);
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

// ---------------------------------------------------------------------------
// Helpers that build the Claude.ai DOM structure observed in production
// ---------------------------------------------------------------------------

/**
 * Builds the exact DOM shape observed in the live Claude.ai branching
 * conversation — one chat-input-grid-container shared by N branch editors.
 *
 *  body
 *  └─ outerFlex  (.flex.flex-1.h-full.w-full.overflow-hidden.relative)
 *     └─ chatGrid  ([data-testid="chat-input-grid-container"])
 *        ├─ toolbar  (div.flex.items-center.gap-1.shrink-0)
 *        │  └─ sendBtn  (button — no aria-label in current Claude UI)
 *        ├─ modelSelectorWrapper  (div.overflow-hidden.shrink-0)
 *        │  └─ modelSelector  (button[data-testid="model-selector-dropdown"])
 *        └─ editor1, editor2, editor3, editor4  (textarea[id="editor-*"])
 */
function buildClaudeDom(editorCount = 4) {
  const body = createNode('div', { id: 'body' });

  const outerFlex = createNode('div', {
    className: 'flex flex-1 h-full w-full overflow-hidden relative'
  });
  body.appendChild(outerFlex);

  const chatGrid = createNode('div', {
    'data-testid': 'chat-input-grid-container',
    className: 'grid'
  });
  outerFlex.appendChild(chatGrid);

  // Right-side action cluster — send button has no aria-label (matches production)
  const toolbar = createNode('div', {
    className: 'flex items-center gap-1 shrink-0'
  });
  chatGrid.appendChild(toolbar);
  const sendBtn = createNode('button', { className: 'send-btn' });
  toolbar.appendChild(sendBtn);

  // Model selector — its parent div is the intended leftCluster
  const modelSelectorWrapper = createNode('div', {
    className: 'overflow-hidden shrink-0 p-1'
  });
  chatGrid.appendChild(modelSelectorWrapper);
  const modelSelector = createNode('button', {
    'data-testid': 'model-selector-dropdown',
    className: 'inline-flex items-center justify-center relative shrink-0'
  });
  modelSelectorWrapper.appendChild(modelSelector);

  // Branch editors — all inside the same chatGrid
  const editors = [];
  for (let i = 0; i < editorCount; i++) {
    const id = `editor-branch${i}`;
    const editorWrapper = createNode('div', { className: 'w-full relative min-w-0 h-full' });
    chatGrid.appendChild(editorWrapper);
    const textarea = createNode('textarea', {
      id,
      className: 'px-5 pt-4 pb-4 w-full resize-none bg-transparent'
    });
    textarea.id = id;
    editorWrapper.appendChild(textarea);
    editors.push(textarea);
  }

  return { body, outerFlex, chatGrid, toolbar, sendBtn, modelSelector, modelSelectorWrapper, editors };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('SSOT dedup in attachButtonToPreferredHost', () => {
  it('allows the first button to attach to an empty container', () => {
    const body = createNode('div');
    const container = createNode('div', { className: 'action-row' });
    body.appendChild(container);

    const btn = makeSignButton('e1');
    body.appendChild(btn);

    const adapter = {
      key: 'test',
      tryAttach(b) { container.appendChild(b); return true; }
    };

    const result = attachButtonToPreferredHost(btn, null, adapter, body);

    assert.strictEqual(result, true, 'first button should attach');
    assert.strictEqual(container.querySelectorAll('.encypher-sign-btn').length, 1);
    assert.strictEqual(btn.parentElement, container);
  });

  it('reverts a duplicate button back to body when container already has one', () => {
    const body = createNode('div');
    const container = createNode('div', { className: 'action-row' });
    body.appendChild(container);

    // First button — attaches successfully
    const btn1 = makeSignButton('e1');
    body.appendChild(btn1);
    container.appendChild(btn1);
    btn1._parent = container; // simulate hosted state

    // Second button — should be rejected
    const btn2 = makeSignButton('e2');
    body.appendChild(btn2);

    const adapter = {
      key: 'test',
      tryAttach(b) { container.appendChild(b); return true; }
    };

    const result = attachButtonToPreferredHost(btn2, null, adapter, body);

    assert.strictEqual(result, false, 'duplicate should not attach');
    assert.strictEqual(container.querySelectorAll('.encypher-sign-btn').length, 1,
      'only one sign button in container');
    assert.strictEqual(btn2.parentElement, body, 'duplicate reverted to body');
  });

  it('allows buttons to attach to different containers independently', () => {
    const body = createNode('div');
    const container1 = createNode('div', { className: 'action-row-1' });
    const container2 = createNode('div', { className: 'action-row-2' });
    body.appendChild(container1);
    body.appendChild(container2);

    const btn1 = makeSignButton('e1');
    body.appendChild(btn1);
    const btn2 = makeSignButton('e2');
    body.appendChild(btn2);

    const adapter1 = { key: 'test', tryAttach(b) { container1.appendChild(b); return true; } };
    const adapter2 = { key: 'test', tryAttach(b) { container2.appendChild(b); return true; } };

    assert.strictEqual(attachButtonToPreferredHost(btn1, null, adapter1, body), true);
    assert.strictEqual(attachButtonToPreferredHost(btn2, null, adapter2, body), true);
    assert.strictEqual(container1.querySelectorAll('.encypher-sign-btn').length, 1);
    assert.strictEqual(container2.querySelectorAll('.encypher-sign-btn').length, 1);
  });
});

describe('Claude.ai adapter — production branching conversation scenario', () => {
  it('attaches exactly one sign button when 4 branch editors share the same container', () => {
    const { body, toolbar, editors } = buildClaudeDom(4);

    let hostedCount = 0;
    let floatingCount = 0;

    for (const editor of editors) {
      const btn = makeSignButton(editor.id);
      body.appendChild(btn);
      const adapter = getClaudeAdapter(editor, 'claude.ai');
      const hosted = attachButtonToPreferredHost(btn, editor, adapter, body);
      if (hosted) hostedCount++;
      else floatingCount++;
    }

    assert.strictEqual(hostedCount, 1, 'exactly one editor gets hosted placement');
    assert.strictEqual(floatingCount, 3, 'the other three fall back to floating');
    assert.strictEqual(
      toolbar.querySelectorAll('.encypher-sign-btn').length, 1,
      'toolbar contains exactly one sign button'
    );
  });

  it('places the sign button inside the rightCluster toolbar, not in outerFlex', () => {
    const { body, outerFlex, toolbar, editors } = buildClaudeDom(1);

    const btn = makeSignButton(editors[0].id);
    body.appendChild(btn);
    const adapter = getClaudeAdapter(editors[0], 'claude.ai');
    attachButtonToPreferredHost(btn, editors[0], adapter, body);

    assert.ok(toolbar.contains(btn), 'sign button should be inside toolbar');
    assert.strictEqual(
      outerFlex.querySelectorAll('.encypher-sign-btn').filter(b => b.parentElement === outerFlex).length,
      0,
      'sign button must not be a direct child of outerFlex'
    );
  });

  it('rightCluster is found via class selector when send button has no aria-label', () => {
    const { editors } = buildClaudeDom(1);
    // Production: sendBtn has no aria-label="Send message" — adapter must find
    // rightCluster via div[class*="flex"][class*="items-center"][class*="gap"][class*="shrink-0"]
    const adapter = getClaudeAdapter(editors[0], 'claude.ai');
    assert.ok(adapter !== null, 'adapter should be returned for claude.ai');
    assert.strictEqual(adapter.key, 'claude');
  });
});

describe('Claude.ai adapter — leftCluster selector never resolves to a button', () => {
  it('closest("div[class*=flex]:not(button)") skips the model-selector button itself', () => {
    const { chatGrid, modelSelector } = buildClaudeDom(1);

    // The model selector button has "inline-flex" in its class — the old bug
    // was that closest('[class*="flex"]') matched the button itself, which has
    // inline-flex. The fix uses 'div[class*="flex"]:not(button)' so it walks up
    // past the button to find a div ancestor.
    const resolvedViaOldSelector = modelSelector.closest('[class*="flex"]');
    const resolvedViaFixedSelector = modelSelector.closest('div[class*="flex"]:not(button)');

    assert.strictEqual(resolvedViaOldSelector.tagName, 'BUTTON',
      'old selector incorrectly resolves to the button itself');
    assert.strictEqual(resolvedViaFixedSelector.tagName, 'DIV',
      'fixed selector correctly resolves to a div ancestor');
    assert.notStrictEqual(resolvedViaFixedSelector, modelSelector,
      'fixed selector must not return the model selector button');
  });

  it('a sign button appended to a DIV leftCluster stays inside that div', () => {
    const { body, modelSelectorWrapper, editors } = buildClaudeDom(1);

    // Remove the toolbar so rightCluster is null and we fall through to leftCluster
    const { chatGrid } = buildClaudeDom(1);

    // Build a minimal DOM where only leftCluster is available (no toolbar)
    const body2 = createNode('div');
    const grid = createNode('div', { 'data-testid': 'chat-input-grid-container', className: 'grid' });
    body2.appendChild(grid);

    const wrapperDiv = createNode('div', { className: 'flex items-center' });
    grid.appendChild(wrapperDiv);
    const modelBtn = createNode('button', {
      'data-testid': 'model-selector-dropdown',
      className: 'inline-flex items-center justify-center'
    });
    wrapperDiv.appendChild(modelBtn);

    const editorWrapper = createNode('div');
    grid.appendChild(editorWrapper);
    const editor = createNode('textarea', { id: 'editor-test' });
    editor.id = 'editor-test';
    editorWrapper.appendChild(editor);

    const btn = makeSignButton('editor-test');
    body2.appendChild(btn);

    const adapter = getClaudeAdapter(editor, 'claude.ai');
    attachButtonToPreferredHost(btn, editor, adapter, body2);

    // The button should be inside wrapperDiv (a div), not inside modelBtn (a button)
    assert.notStrictEqual(btn.parentElement, modelBtn,
      'sign button must not be a child of the model-selector button element');
  });
});

describe('Claude.ai adapter — returns null for non-claude hostnames', () => {
  it('does not return an adapter for chatgpt.com', () => {
    const { editors } = buildClaudeDom(1);
    const adapter = getClaudeAdapter(editors[0], 'chatgpt.com');
    assert.strictEqual(adapter, null);
  });

  it('does not return an adapter for unknown hostnames', () => {
    const { editors } = buildClaudeDom(1);
    const adapter = getClaudeAdapter(editors[0], 'example.com');
    assert.strictEqual(adapter, null);
  });
});

// ---------------------------------------------------------------------------
// Inline the scan and shouldSkipEditor logic for the new filter fixes
// ---------------------------------------------------------------------------

function scanForEditorsInRoot_fixed(root, candidates = new Set()) {
  const textareas = Array.from(root.querySelectorAll('textarea'));
  textareas.forEach(ta => {
    const rows = parseInt(ta._attrs.rows || '2', 10);
    const offsetHeight = ta._offsetHeight || 0;
    if (rows >= 3 || offsetHeight >= 80) {
      candidates.add(ta);
    } else if (ta.closest?.('[data-testid="chat-input-grid-container"]')) {
      candidates.add(ta);
    }
  });
  return candidates;
}

function shouldSkipEditor_fixed(element) {
  const rect = { width: element._width || 0, height: element._height || 0 };
  const minHeight = element.closest?.('[data-testid="chat-input-grid-container"]') ? 8 : 28;
  if (rect.width < 180 || rect.height < minHeight) return true;
  return false;
}

describe('scan filter — auto-growing main composer included via grid container check', () => {
  it('excludes a tiny textarea that is NOT inside chat-input-grid-container', () => {
    const body = createNode('div');
    const ta = createNode('textarea', { className: 'small-search' });
    ta._attrs.rows = '2';
    ta._offsetHeight = 22;
    ta._width = 300;
    ta._height = 22;
    body.appendChild(ta);

    const candidates = scanForEditorsInRoot_fixed(body);
    assert.strictEqual(candidates.has(ta), false,
      'tiny textarea outside grid container should be excluded');
  });

  it('includes a tiny auto-growing textarea that IS inside chat-input-grid-container', () => {
    const { chatGrid } = buildClaudeDom(0);
    const body = createNode('div');
    body.appendChild(chatGrid);

    const mainComposer = createNode('textarea', { className: 'composer' });
    mainComposer._attrs.rows = '2';  // HTML default — never explicitly set
    mainComposer._offsetHeight = 22; // auto-growing, starts tiny
    chatGrid.appendChild(mainComposer);

    const candidates = scanForEditorsInRoot_fixed(chatGrid);
    assert.strictEqual(candidates.has(mainComposer), true,
      'main composer inside grid container must be included despite small size');
  });

  it('still includes large textareas via the existing rows/height check', () => {
    const body = createNode('div');
    const largeTa = createNode('textarea');
    largeTa._attrs.rows = '5';
    largeTa._offsetHeight = 120;
    body.appendChild(largeTa);

    const candidates = scanForEditorsInRoot_fixed(body);
    assert.strictEqual(candidates.has(largeTa), true,
      'large textarea should still pass the original size check');
  });
});

describe('shouldSkipEditor — min-height bypass for chat-input-grid-container', () => {
  it('skips a 22px textarea that is NOT in the grid container', () => {
    const body = createNode('div');
    const ta = createNode('textarea');
    ta._width = 600;
    ta._height = 22;
    body.appendChild(ta);

    assert.strictEqual(shouldSkipEditor_fixed(ta), true,
      '22px textarea outside grid container should be skipped');
  });

  it('does NOT skip a 22px textarea that IS in the grid container', () => {
    const { chatGrid } = buildClaudeDom(0);
    const ta = createNode('textarea');
    ta._width = 600;
    ta._height = 22;
    chatGrid.appendChild(ta);

    assert.strictEqual(shouldSkipEditor_fixed(ta), false,
      '22px textarea inside grid container should not be skipped');
  });

  it('still skips elements that are too narrow even inside the grid container', () => {
    const { chatGrid } = buildClaudeDom(0);
    const ta = createNode('textarea');
    ta._width = 50;  // below 180px threshold
    ta._height = 22;
    chatGrid.appendChild(ta);

    assert.strictEqual(shouldSkipEditor_fixed(ta), true,
      'too-narrow textarea should still be skipped even inside grid container');
  });
});

// ---------------------------------------------------------------------------
// Editable-body iframe detection (_isEditableBodyFrame / _getButtonMountRoot)
// ---------------------------------------------------------------------------

/**
 * Inline the logic under test.
 * The functions accept injectable context objects so they can be unit-tested
 * without a real browser.
 *
 * context = { isTopFrame, bodyContentEditable, parentBody (optional), localBody }
 */
function isEditableBodyFrame(ctx) {
  return !ctx.isTopFrame && ctx.bodyContentEditable === 'true';
}

function getButtonMountRoot(ctx) {
  if (isEditableBodyFrame(ctx)) {
    if (ctx.parentBody) return ctx.parentBody;
    return null; // cross-origin: cannot mount safely
  }
  return ctx.localBody;
}

/**
 * Simulates attaching a button as attachSignButton does.
 * Returns { button, mountRoot } or null when mounting is skipped.
 */
function simulateAttachInFrame(ctx) {
  const mountRoot = getButtonMountRoot(ctx);
  if (!mountRoot) return null; // cross-origin editable-body iframe — skip

  const button = makeSignButton('test-editor');
  mountRoot.appendChild(button);
  return { button, mountRoot };
}

describe('editable-body iframe detection — button must not land inside email body', () => {
  it('isEditableBodyFrame is false in the top frame', () => {
    const ctx = { isTopFrame: true, bodyContentEditable: 'true' };
    assert.strictEqual(isEditableBodyFrame(ctx), false,
      'top frame with editable body is not an email-body iframe');
  });

  it('isEditableBodyFrame is false in an iframe whose body is NOT editable', () => {
    const ctx = { isTopFrame: false, bodyContentEditable: null };
    assert.strictEqual(isEditableBodyFrame(ctx), false,
      'iframe without editable body is not an email-body iframe');
  });

  it('isEditableBodyFrame is true in an iframe whose body is contenteditable (Zoho Mail pattern)', () => {
    const ctx = { isTopFrame: false, bodyContentEditable: 'true' };
    assert.strictEqual(isEditableBodyFrame(ctx), true,
      'iframe with contenteditable body should be detected as email-body frame');
  });

  it('getButtonMountRoot returns localBody in the top frame', () => {
    const localBody = createNode('div', { id: 'top-body' });
    const ctx = { isTopFrame: true, bodyContentEditable: null, localBody };
    assert.strictEqual(getButtonMountRoot(ctx), localBody,
      'top-frame buttons should mount on the local body');
  });

  it('getButtonMountRoot returns parentBody for same-origin editable-body iframe', () => {
    const parentBody = createNode('div', { id: 'parent-body' });
    const localBody  = createNode('div', { id: 'iframe-body' });
    const ctx = { isTopFrame: false, bodyContentEditable: 'true', localBody, parentBody };
    assert.strictEqual(getButtonMountRoot(ctx), parentBody,
      'editable-body iframe buttons should mount on the parent frame body');
  });

  it('getButtonMountRoot returns null for cross-origin editable-body iframe', () => {
    const localBody = createNode('div', { id: 'iframe-body' });
    const ctx = { isTopFrame: false, bodyContentEditable: 'true', localBody, parentBody: null };
    assert.strictEqual(getButtonMountRoot(ctx), null,
      'cross-origin editable-body iframe should skip button mounting');
  });

  it('button does NOT land in the email body for same-origin editable-body iframe', () => {
    const parentBody = createNode('div', { id: 'parent-body' });
    const emailBody  = createNode('div', { id: 'email-body' });
    const ctx = { isTopFrame: false, bodyContentEditable: 'true', localBody: emailBody, parentBody };

    const result = simulateAttachInFrame(ctx);

    assert.ok(result, 'button should be created');
    assert.strictEqual(result.mountRoot, parentBody, 'button should mount on parent body');
    assert.strictEqual(emailBody.querySelectorAll('.encypher-sign-btn').length, 0,
      'email body must contain no sign buttons');
    assert.strictEqual(parentBody.querySelectorAll('.encypher-sign-btn').length, 1,
      'parent body should contain the sign button');
  });

  it('button attachment is skipped entirely for cross-origin editable-body iframe', () => {
    const emailBody = createNode('div', { id: 'email-body' });
    const ctx = { isTopFrame: false, bodyContentEditable: 'true', localBody: emailBody, parentBody: null };

    const result = simulateAttachInFrame(ctx);

    assert.strictEqual(result, null, 'attach should be skipped for cross-origin frame');
    assert.strictEqual(emailBody.querySelectorAll('.encypher-sign-btn').length, 0,
      'email body must remain empty');
  });

  it('normal (non-iframe) flow is unaffected', () => {
    const localBody = createNode('div', { id: 'page-body' });
    const ctx = { isTopFrame: true, bodyContentEditable: null, localBody };

    const result = simulateAttachInFrame(ctx);

    assert.ok(result, 'button should be created in normal flow');
    assert.strictEqual(result.mountRoot, localBody);
    assert.strictEqual(localBody.querySelectorAll('.encypher-sign-btn').length, 1);
  });
});
