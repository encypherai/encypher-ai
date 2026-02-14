# PRD: Selection Signing, Smart Backspace, Embedding Provenance

## Status: COMPLETE
## Current Goal: All tasks complete

## Overview
Three enhancements to the Chrome extension's signing and editing workflow:
1. Users can sign any selected text on screen (in-place replacement when editable, clipboard fallback otherwise)
2. When a user presses backspace into an embedding byte string, auto-delete the entire embedding to avoid invisible character confusion
3. Store deleted/replaced embeddings as provenance so re-signing can build a chain of custody

Additionally, design (PRD-only) native Google Docs add-on and MS Office add-in for deeper integration.

## Objectives
- Sign selected text in-place (editable contexts) or to clipboard (read-only contexts)
- Add keyboard shortcut (Ctrl+Shift+E) for signing selection
- Detect backspace into embedding bytes and auto-delete the full embedding run
- Store previous embeddings in local storage as provenance metadata
- Pass provenance chain to sign API when re-signing content
- Design spec for native Google Docs / MS Office plugins

## Tasks

### 1.0 Sign Selected Content
- [x] 1.1 Enhance handleSignSelection to replace selection in-place when in editable element — ✅ node --test
- [x] 1.2 Add keyboard shortcut (Ctrl+Shift+E) for sign-selection — ✅ node --test
- [x] 1.3 replaceSelectionInPlace for textarea/input and contenteditable — ✅ node --test
- [x] 1.4 Fallback to clipboard when selection is in read-only context — ✅ node --test

### 2.0 Smart Backspace
- [x] 2.1 Add keydown listener (capture phase) for Backspace/Delete — ✅ node --test
- [x] 2.2 findEmbeddingRun detects cursor adjacent to embedding bytes — ✅ node --test
- [x] 2.3 Auto-delete entire embedding run (ZWNBSP + VS sequence) — ✅ node --test
- [x] 2.4 Show brief notification that embedding was removed — ✅ node --test
- [x] 2.5 Store removed embedding bytes as provenance before deletion — ✅ node --test

### 3.0 Embedding Provenance Chain
- [x] 3.1 Define provenance storage schema (chrome.storage.local, capped at 50 keys) — ✅ node --test
- [x] 3.2 storeProvenance + getProvenance for embedding bytes + metadata — ✅ node --test
- [x] 3.3 Pass previous_embeddings to sign API via service worker — ✅ node --test
- [x] 3.4 Provenance lookup uses visible text hash (strips embedding chars) — ✅ node --test

### 4.0 Native Plugin Design (PRD only)
- [x] 4.1 Write design spec for Google Docs add-on (Apps Script) — PRD_Native_Editor_Plugins_Design.md
- [x] 4.2 Write design spec for MS Office add-in (Office.js) — PRD_Native_Editor_Plugins_Design.md

### 5.0 Tests
- [x] 5.1 Tests for in-place selection signing (2 tests) — ✅ node --test
- [x] 5.2 Tests for smart backspace embedding detection (17 tests) — ✅ node --test
- [x] 5.3 Tests for provenance storage and retrieval (2 tests) — ✅ node --test
- [x] 5.4 All existing tests still pass: 80/80 (56 existing + 24 new) — ✅ node --test

## Success Criteria
- User can select text, right-click → Sign, and see it replaced in-place (editable) or copied (read-only)
- Ctrl+Shift+E signs selected text
- Backspace into embedding auto-deletes the whole embedding run
- Provenance chain is stored and passed to sign API
- All tests pass (existing + new)

## Completion Notes
- `handleSignSelection()` replaces old `handleContextMenuSign()` — detects editable context, replaces in-place or falls back to clipboard
- `replaceSelectionInPlace()` handles textarea/input (selectionStart/End) and contenteditable (Range API)
- `handleSmartBackspace()` intercepts Backspace/Delete in capture phase, finds embedding run via `findEmbeddingRun()`, deletes entire run
- `findEmbeddingRun()` expands left/right from cursor to find contiguous ZWNBSP+VS bytes
- `storeProvenance()` / `getProvenance()` use chrome.storage.local, keyed by visible text hash, capped at 50 keys × 10 entries
- `extractRunBytes()` extracts raw byte values from VS characters for provenance storage
- `_stripEmbeddingChars()` removes all VS/ZWNBSP for consistent hashing across signed/unsigned versions
- Service worker passes `previous_embeddings` to sign API request body
- `initSmartBackspace()` and `initSignShortcut()` called from `_initEditorSigner()` (always active, independent of editor buttons)
- Native plugin design specs written for Google Docs (Apps Script) and MS Office (Office.js)
- 80 extension tests pass (24 new)
