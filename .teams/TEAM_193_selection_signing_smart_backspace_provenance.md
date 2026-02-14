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

---

## Microsoft Office Add-in Follow-on (Implemented)

### Scope
- Built a new native Microsoft Office Add-in under `integrations/microsoft-office-addin/` with cross-host support for Word, Excel, and PowerPoint.

### What was implemented
- **Manifest + command surface** (`manifest.xml`):
  - Multi-host configuration: Document (Word), Workbook (Excel), Presentation (PowerPoint)
  - Task pane ribbon buttons for each host
  - Shared task pane source location
- **Task pane UI** (`taskpane/taskpane.html`, `taskpane/taskpane.css`):
  - Actions: sign/verify selection + full-document actions
  - Settings: API key + API base URL
  - Host capability display + provenance summary + JSON result panel
- **Host capability matrix** (`src/host-capabilities.js`):
  - Word: selection + full-document
  - Excel: selection-only
  - PowerPoint: selection-only
- **Host adapters** (`src/host-adapters.js`):
  - Selection read/replace via Common API (`getSelectedDataAsync`, `setSelectedDataAsync`)
  - Word full-document read/replace via `Word.run`
- **Sign/verify/provenance orchestration** (`src/app.js`):
  - Host-aware action routing
  - Sign/verify API integration
  - Previous embedding reuse for re-sign operations
- **API client** (`src/api-client.js`):
  - `/api/v1/sign` and `/api/v1/verify` integration
  - HTTPS + `*.encypherai.com` host enforcement
- **Roaming settings persistence** (`src/storage.js`):
  - User settings and provenance entries in `Office.context.roamingSettings`
  - Index-based provenance key trimming (no reliance on private Office internals)
- **Embedding/provenance utilities** (`src/provenance-utils.js`):
  - VS/ZWNBSP parsing, run extraction, text hashing, capped merge

### Validation
- Added and executed Node tests:
  - `tests/provenance-utils.test.js`
  - `tests/host-capabilities.test.js`
  - `tests/api-client.test.js`
- Test result: **13/13 passing** via `npm test`.

### Documentation
- Added `integrations/microsoft-office-addin/README.md` with:
  - host coverage and current limitations
  - local testing and sideload instructions
  - AppSource readiness checklist

### Suggested Git Commit Message (Microsoft Office Add-in)
```
feat(integrations): add Microsoft Office add-in for Word/Excel/PowerPoint

- create new Office add-in project under integrations/microsoft-office-addin
- add multi-host manifest with task pane command surfaces
- implement host capability matrix and host adapters
- support sign/verify for selection across Word/Excel/PowerPoint
- support full-document sign/verify for Word
- add provenance extraction and roaming-settings chain persistence
- enforce HTTPS + *.encypherai.com API host validation
- add task pane UI for actions, settings, capabilities, and results
- add tests for provenance utils, host capabilities, and API URL policy (13/13 passing)
- add README with sideloading and AppSource checklist
```

---

## Outlook Email Add-in + Embedding Survivability (Implemented)

### Scope
- Built a native Outlook Mailbox add-in scaffold and implemented empirical survivability tests for `micro_ecc_c2pa` vs `zw_embedding` under email-like processor transforms.

### What was implemented
- **Outlook add-in scaffold** under `integrations/outlook-email-addin/`:
  - `manifest.xml` (Mailbox host, compose/read command surfaces)
  - task pane UI (`taskpane/taskpane.html`, `taskpane/taskpane.css`)
  - app orchestration (`src/app.js`)
  - mailbox body adapter (`src/outlook-adapter.js`)
  - API client with strict host validation (`src/api-client.js`)
  - roaming settings + provenance persistence (`src/storage.js`)
  - embedding/provenance utilities (`src/provenance-utils.js`)
- **Email survivability harness** (`src/survivability-harness.js`):
  - transform scenarios: identity, unicode NFC, strip supplementary VS, strip all VS, strip format controls
  - viability thresholds: VS run >= 44 (micro_ecc marker), zero-width run >= 128
- **Outlook harness tests**:
  - `tests/provenance-utils.test.js`
  - `tests/api-client.test.js`
  - `tests/survivability-harness.test.js`
- **Enterprise API survivability tests**:
  - `enterprise_api/tests/test_email_embedding_survivability.py`
  - uses real `vs256_rs_crypto` and `zw_crypto` sign/verify utilities
- **Documentation**:
  - `integrations/outlook-email-addin/README.md`
  - `docs/architecture/EMAIL_EMBEDDING_SURVIVABILITY_MATRIX.md`
  - `PRDs/CURRENT/PRD_Outlook_Email_Addin_and_Embedding_Survivability.md`

### Validation
- `npm test` in `integrations/outlook-email-addin`: **14/14 passing**
- `uv run pytest enterprise_api/tests/test_email_embedding_survivability.py -q`: **5/5 passing**

### Survivability findings (simulated processors)
- `micro_ecc_c2pa` survives identity/NFC and format-control stripping, but fails when variation selectors are stripped.
- `zw_embedding` survives identity/NFC and variation-selector stripping, but fails when aggressive format-control stripping is applied.
- Conclusion: no single invisible method is universal across all email processors.

### Default strategy recommendation
- Default to **`micro_ecc_c2pa`** for compactness + RS error correction.
- Add dynamic fallback to **`zw_embedding`** for known VS-stripping domains/processors.
- Keep verification fallback attempting both marker families.

### Suggested Git Commit Message (Outlook + Survivability)
```
feat(integrations): add Outlook email add-in and embedding survivability harness

- create Outlook Mailbox add-in scaffold with compose/read task pane support
- implement email body sign/verify flow with Encypher API integration
- add roaming-settings persistence for API settings and provenance chain
- enforce https + *.encypherai.com API host validation
- add JS survivability harness comparing micro_ecc_c2pa vs zero-width embeddings
- add Python enterprise tests for email transform survivability with real crypto utilities
- add survivability matrix documentation and Outlook sideloading README
- test status: outlook npm tests 14/14, enterprise pytest 5/5
```

### Branding / Design Standards Pass (Completed)
- Updated Outlook task pane UI content and hierarchy to match Encypher brand voice:
  - standards authority framing (C2PA Section A.7)
  - proof-of-origin messaging
  - collaborative infrastructure positioning
- Applied official Encypher palette and typography guidance from
  `docs/company_internal_strategy/Encypher_Marketing_Guidelines.md`.
- Updated manifest display metadata and ribbon command copy for brand consistency.
- Verified UI rendering via Puppeteer (screenshot + DOM token checks).

### Suggested Git Commit Message (Branding Completion)
```
feat(outlook-addin): align UI and manifest with Encypher brand standards

- apply official Encypher color system and Roboto-first typography in task pane
- add standards-authority and proof-of-origin hero/trust messaging
- refine action/settings copy for collaborative C2PA positioning
- update Outlook manifest display name/description and command labels
- update README and PRD notes for brand-guideline conformance
- verify UI via Puppeteer screenshot and style/content checks
```
