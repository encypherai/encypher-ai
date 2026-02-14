# TEAM_193 - Selection Signing, Smart Backspace, Embedding Provenance

## Status: COMPLETE

## Summary
Three enhancements: (1) sign selected text in-place or to clipboard, (2) smart backspace that auto-deletes entire embedding byte runs, (3) provenance chain storage for re-signing. Plus design spec for native Google Docs/MS Office plugins.

## Changes Made

### Sign Selected Content In-Place
- `handleSignSelection()` replaces old `handleContextMenuSign()` — detects if selection is in an editable element
- `replaceSelectionInPlace()` — handles textarea/input (selectionStart/End API) and contenteditable (Range API)
- Falls back to clipboard copy when selection is in read-only context
- Keyboard shortcut: **Ctrl+Shift+E** to sign selected text
- Provenance-aware: looks up previous embeddings before signing, passes them to API

### Smart Backspace
- `handleSmartBackspace()` — keydown listener in capture phase for Backspace/Delete
- `findEmbeddingRun(text, cursorPos)` — expands left/right from cursor to find contiguous ZWNBSP+VS byte run
- Auto-deletes entire embedding run when user backspaces into it
- Shows "Embedding removed" notification
- Stores deleted embedding bytes as provenance before deletion

### Embedding Provenance Chain
- `storeProvenance(visibleTextHash, bytes, metadata)` — stores in chrome.storage.local
- `getProvenance(visibleTextHash)` — retrieves provenance chain for content
- Keyed by visible text hash (strips embedding chars for consistent matching)
- Capped at 50 keys × 10 entries per key
- `extractRunBytes(text)` — extracts raw byte values from VS characters
- `_stripEmbeddingChars(text)` — removes all VS/ZWNBSP for hashing
- Service worker passes `previous_embeddings` to sign API request body

### Embedding Byte Utilities
- `_isVS(cp)` / `_isEmbeddingChar(cp)` — mirrors detector.js VS range constants
- `VS_RANGES` / `ZWNBSP` constants shared with detector

### Native Plugin Design Specs
- Google Docs Add-on: Apps Script + DocumentApp API + sidebar UI
- MS Office Add-in: Office.js + React task pane + Word.js API

## Test Results
- **Extension tests**: 80/80 pass (56 existing + 24 new)
- New test suites: Variation Selector Detection, extractRunBytes, findEmbeddingRun, _stripEmbeddingChars, Provenance Storage Schema, Selection Signing Flow, Keyboard Shortcut

## Files Changed
- `content/editor-signer.js` — Add embedding byte detection, provenance storage, smart backspace, sign-selection in-place, keyboard shortcut
- `background/service-worker.js` — Pass previous_embeddings to sign API
- `tests/editor-signer.test.js` — Add 24 new tests
- `PRDs/CURRENT/PRD_Selection_Signing_Smart_Backspace_Provenance.md` — NEW PRD (complete)
- `PRDs/CURRENT/PRD_Native_Editor_Plugins_Design.md` — NEW design spec for native plugins

## Suggested Git Commit Message
```
feat(extension): sign selection in-place, smart backspace, provenance chain

- Add handleSignSelection() with in-place replacement for editable contexts
- Add replaceSelectionInPlace() for textarea/input and contenteditable
- Add Ctrl+Shift+E keyboard shortcut for signing selected text
- Add smart backspace: auto-delete entire embedding byte run on Backspace/Delete
- Add findEmbeddingRun() to detect contiguous ZWNBSP+VS sequences at cursor
- Add embedding provenance chain storage (chrome.storage.local, capped)
- Store deleted/replaced embedding bytes as provenance for re-signing
- Pass previous_embeddings to sign API for provenance chain building
- Add design specs for native Google Docs add-on and MS Office add-in
- Add 24 new tests for embedding detection, provenance, and signing (80/80 total)
```

---

## Google Docs Add-on Follow-on (Implemented)

### Scope
- Built a new native Google Docs Add-on under `integrations/google-docs-addon/` per Google Workspace Add-on requirements.

### What was implemented
- **Apps Script manifest** (`appsscript.json`) with:
  - add-on metadata (`addOns.common`, `addOns.docs`)
  - required scopes (`documents.currentonly`, `script.container.ui`, `script.external_request`, `userinfo.email`)
  - API URL allowlist (`urlFetchWhitelist` for `https://api.encypherai.com/`)
- **Entry points + menu actions** (`Code.gs`):
  - `onInstall`, `onOpen`, add-on homepage card, sidebar launch
  - Docs add-on menu: Open Sidebar, Sign Selection/Document, Verify Selection/Document
- **Core Docs workflows** (`DocsService.gs`):
  - selection/full-doc extraction
  - selection/full-doc sign and replace
  - selection/full-doc verification
- **API integration** (`Api.gs`):
  - sign via `/api/v1/sign`
  - verify via `/api/v1/verify`
  - robust HTTP and JSON error handling
- **Provenance chain** (`Provenance.gs`):
  - VS/ZWNBSP embedding extraction
  - per-document provenance persistence + capping
  - reuse as `previous_embeddings` during re-sign
- **Settings + sidebar actions** (`SidebarActions.gs`):
  - save/clear API key + base URL
  - runtime state + provenance summary
- **Security policy** (`Config.gs`):
  - enforced HTTPS and `*.encypherai.com` API base URL policy
- **UI** (`Sidebar.html`):
  - branded Encypher sidebar for sign/verify/settings/provenance

### Validation
- Added local Node tests for provenance utility logic:
  - `integrations/google-docs-addon/tests/provenance-utils.test.js`
- Test result: **6/6 passing** via `npm test` in `integrations/google-docs-addon`.

### Documentation and deployment
- Added `integrations/google-docs-addon/README.md` with:
  - setup, testing, clasp deploy instructions
  - Marketplace submission checklist
- Added `.clasp.json.example`, `.claspignore`, `.gitignore`, `package.json` for local test workflow.

### Suggested Git Commit Message (Google Docs Add-on)
```
feat(integrations): add native Google Docs add-on with sign/verify and provenance chain

- Create Apps Script Google Docs add-on scaffold under integrations/google-docs-addon
- Add compliant appsscript.json manifest with docs add-on metadata and scopes
- Implement Docs menu + sidebar entrypoints (onOpen/onInstall/homepage card)
- Add sign/verify flows for selection and full document via Encypher API
- Add provenance extraction/storage and reuse via previous_embeddings
- Enforce HTTPS + *.encypherai.com API base URL policy for add-on settings
- Add local Node tests for provenance utilities (6/6 passing)
- Add README with clasp deployment and Marketplace checklist
```
