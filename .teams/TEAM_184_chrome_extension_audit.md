# TEAM_184 — Chrome Extension Full Audit & Feature Verification

## Session Goal
Audit the Chrome extension codebase for bugs, ensure all features work, and test against WordPress docker instance with signed content.

## Status: COMPLETE

## Critical Bug Fixed

### `extractEmbeddedBytes` used wrong encoding scheme (SHOWSTOPPER)
The detector used a **nibble-based** approach (two VS1 chars = 1 byte) but the actual `c2pa_text` standard uses **one VS per byte**:
- VS1 (FE00-FE0F) → bytes 0-15
- VS2 (E0100-E01EF) → bytes 16-255

This meant the extension **could never detect real signed content** from the WordPress plugin or any other c2pa_text-based signer. Fixed in `detector.js`.

### `scanPage` didn't find ZWNBSP-prefixed wrappers
The old code extracted bytes from scattered VS chars across text nodes. Real C2PA wrappers are ZWNBSP-prefixed contiguous VS sequences. Added `findWrappers()` function that properly locates `ZWNBSP + VS*` sequences and checks their header for C2PA/Encypher magic. Legacy fallback retained for non-wrapper embeddings.

## Other Bugs Fixed

1. **`service-worker.js` — `updateIcon` hardcoded `icons.found`**: The icon state never changed. Also referenced non-existent colored icon variants (icon16-green.png etc.). Fixed to use base icons for all states and rely on badge text + badge color for state indication.
2. **`service-worker.js` — `revoked` hardcoded to `false`**: Now reads `verdict.revoked` and `verdict.revoked_at` from API response. Also propagated to top-level result.
3. **`detector.js` — Badge re-injection blocked by existing badge**: `injectBadge` returned early if any badge existed, preventing pending→verified transitions. Now removes existing badges (but won't downgrade non-pending to pending).
4. **`popup.js` — `DOMContentLoaded` race**: Script loaded at end of body, so event may have already fired. Added `readyState` check.
5. **`options.js` — Same `DOMContentLoaded` race**: Same fix applied.
6. **`e2e/extension.test.js` — `page` variable undefined**: Used `page.on('dialog')` but variable was `options`. Fixed to use `options` and moved dialog handler before the click.
7. **`e2e/extension.test.js` — Tab count assertion wrong**: Asserted 2 tabs but there are 3 (Verify, Sign, Debug). Fixed to 3.
8. **`detector.js` — `markerType` missing from badge details**: Added `markerType` and `organizationId` to all badge detail paths (verified/invalid/revoked/error).

## Enhancements

1. **`manifest.json` — Added `localhost:8000` host permission**: Full-stack runs on port 8000 via Traefik; extension couldn't reach it.
2. **`options.html` — Added `localhost:8000` dropdown option**: "Local Full-Stack (localhost:8000)" alongside existing standalone option.
3. **`options.js` — Recognize `localhost:8000` as known URL**: Prevents it from falling through to "custom" in settings load.
4. **`test-page.html` — Updated for dual-port support**: Health check tries port 8000 first, then 9000. Checklist updated.

## Test Results
- **38 unit tests pass** (up from 34 — added 4 new tests for `findWrappers`, mixed VS1/VS2, etc.)
- **WordPress live verification confirmed**: Fetched signed article (post 84) from WordPress on port 8888, `findWrappers` correctly finds C2PA wrapper (1785 bytes, magic=C2PATXT\0), API verify returns `valid: true` with full C2PA assertions.

## Files Changed
- `integrations/chrome-extension/content/detector.js` — Critical encoding fix, findWrappers, badge improvements
- `integrations/chrome-extension/background/service-worker.js` — Icon fix, revoked propagation
- `integrations/chrome-extension/popup/popup.js` — DOMContentLoaded race fix
- `integrations/chrome-extension/options/options.js` — DOMContentLoaded race fix, localhost:8000 support
- `integrations/chrome-extension/options/options.html` — localhost:8000 dropdown
- `integrations/chrome-extension/manifest.json` — localhost:8000 host permission
- `integrations/chrome-extension/tests/detector.test.js` — Updated for c2pa_text encoding, new tests
- `integrations/chrome-extension/tests/e2e/extension.test.js` — Bug fixes (page→options, tab count)
- `integrations/chrome-extension/tests/fixtures/test-page.html` — Dual-port support

## Remaining Work / Manual Testing Needed
- **Load extension in Chrome** and visit `http://localhost:8888/?p=84` to visually confirm badge appears
- **Test signing flow** — needs a valid API key (demo-local-key rejected by API gateway for /sign)
- **E2E tests** require Chrome with extension loaded (Puppeteer headful mode) — can't run in this environment
- **Context menu verification** — manual test needed

## Suggested Git Commit Message
```
fix(chrome-ext): critical detection fix — align VS encoding with c2pa_text standard

BREAKING: extractEmbeddedBytes now uses one-VS-per-byte encoding
(VS1→bytes 0-15, VS2→bytes 16-255) matching the c2pa_text reference
implementation. The old nibble-based approach could never detect real
signed content from WordPress or any c2pa_text-based signer.

Also fixes:
- Add findWrappers() for proper ZWNBSP-prefixed wrapper detection
- Fix updateIcon using hardcoded icons.found instead of computed state
- Fix revoked status hardcoded to false (now reads from API response)
- Fix badge re-injection blocking pending→verified transitions
- Fix DOMContentLoaded race in popup.js and options.js
- Fix e2e test: undefined 'page' variable, wrong tab count assertion
- Add localhost:8000 (Traefik full-stack) to host_permissions & options
- Pass markerType through to all badge detail paths

Tests: 38 pass (was 34), verified against live WordPress signed content
```
