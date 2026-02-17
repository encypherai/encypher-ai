# Encypher Chrome Extension User Journeys

## Purpose

This document captures two core user journeys and maps them to current extension behavior:

1. Reader / Verifier (no account required)
2. Publisher / Creator (logged-in or API-key configured)

It also defines how we verify these journeys in automated tests.

---

## Journey A: Reader / Verifier (No Account)

### Who they are
A journalist, researcher, editor, or reader who wants authenticity signals while browsing, without creating an account.

### End-to-end flow
1. Installs extension from Chrome Web Store.
2. Browses normally; extension scans for signed text embeddings.
3. On pages with no signatures, sees neutral/empty state.
4. On pages with signatures:
   - icon badge changes state
   - inline badges appear on detected content
   - popup shows verify summary and detailed statuses (verified / invalid / revoked)
5. User can rescan and inspect verification details quickly from popup.

### Privacy model for this journey
- Verification only sends signed text blocks, not full page content.
- Discovery events are sent only when signed content is found/verified.
- Discovery payload is designed to avoid personal identity data.
- Local cache reduces repeat API calls.

### What this user gets
- Trust signal at browse-time.
- Fast authenticity checks without account setup.
- Passive contribution to content discovery network.

---

## Journey B: Publisher / Creator (Onboarded / API Key)

### Who they are
A writer, journalist, or publisher who needs portable provenance for content across platforms.

### End-to-end flow
1. Installs extension.
2. Opens Sign tab:
   - no key state prompts optional onboarding (email-based setup) or manual API key.
3. Completes onboarding or enters API key.
4. Optionally configures signing defaults in Settings:
   - **Embedding Mode**: *Standard* (micro default: C2PA + error-corrected embeddings) or *Compact* (no embedded C2PA).
   - **Embedding Frequency**: How often signatures are placed in the text (*Entire content*, *Per section*, *Per paragraph*, *Per sentence* (default), or *Per word*).
5. Signs content via:
   - popup sign form (shows embedding mode + frequency dropdowns), and/or
   - inline editor modal (shows same dropdowns, pre-filled from settings), and/or
   - context menu ("Sign with Encypher") using stored defaults, and/or
   - keyboard shortcut Ctrl+Shift+E using stored defaults.
6. Signed text is inserted back into editor while preserving formatting where possible.
7. Published content later appears as verifiable to Reader journey users.

### Signing options
- **Embedding Mode** (API request options):
  - *Standard* (`manifest_mode='micro'`): unified micro defaults (`ecc=true`, `embed_c2pa=true`) for error-corrected segment embeddings + embedded C2PA provenance manifest.
  - *Compact* (`manifest_mode='micro'`, `embed_c2pa=false`): keeps micro markers and DB-backed C2PA manifest but omits in-content C2PA embedding.
- **Embedding Frequency** (`segmentation_level` API parameter):
  - Controls granularity: `document` (one signature), `section`, `paragraph`, `sentence` (default), or `word` (Enterprise).
  - More frequent = more resilient to partial edits but more invisible characters embedded.
- Defaults are persisted in `chrome.storage.sync` and pre-fill all signing surfaces. Users can override per-signing from the popup or inline editor modal.

### Signing robustness in current implementation
- Embedding-plan aware signing request is always enabled.
- Signed output fallback chain:
  1. `signed_text`
  2. `embedded_content`
  3. embedding plan reconstruction
- DOM-preserving insertion strategy:
  - primary: selection-based in-place marker insertion
  - editor fallback: Google Docs / Office Online root-based insertion
  - hardening: normalized matching for NBSP/newline/tab segmentation drift
  - safety fallback: full signed-text replace, then clipboard

### What this user gets
- Universal browser-based signing across web editors.
- Verified feedback loop after publishing.
- Foundation for downstream discovery and enforcement workflows.

---

## Convergence / Network Effect

- Reader users increase discovery coverage by browsing signed pages.
- Publisher users increase signed-content supply.
- Together, they improve trust visibility and discovery density over time.

---

## Verification Matrix (Current)

### Reader / Verifier coverage
- Auto detection + popup verify status and details: implemented.
- Revoked/mixed verification visibility: implemented.
- Retry/dedupe/cache for verification reliability: implemented.
- Discovery tracking on verification events: implemented.

### Publisher / Creator coverage
- Optional onboarding + auto-provision API key: implemented.
- Manual API key path: implemented.
- Sign tab and editor/context signing: implemented.
- DOM-preserving embedding insertion with online editor fallback: implemented.

### Important note
Some product-story elements (for example, explicit per-card "View verification" links or sentence-level diff highlights in popup) may be roadmap enhancements depending on desired UX depth. The core journeys above are operationally supported.

---

## Automated Validation Commands

From `integrations/chrome-extension/`:

```bash
npm test
npm run lint
npm run test:e2e
```

Recommended targeted checks:

```bash
node --test tests/onboarding-setup-flow.test.js
node --test tests/editor-signer-embedding-plan.test.js
node --test tests/e2e/*.test.js
```

---

## Source Pointers

- Extension overview and features: `README.md`
- Privacy and discovery data policy: `PRIVACY.md`
- Popup verify/sign behavior: `popup/popup.html`, `popup/popup.js`
- Background verification/signing/onboarding flow: `background/service-worker.js`
- Editor signing + DOM-preserving insertion: `content/editor-signer.js`
- E2E flow coverage: `tests/e2e/extension.test.js`
- Onboarding setup coverage: `tests/onboarding-setup-flow.test.js`
