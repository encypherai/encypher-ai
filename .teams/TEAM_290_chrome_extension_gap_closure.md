# TEAM_290 - Chrome Extension v2.0.0 Gap Closure

## Session
- Date: 2026-03-30
- Objective: Close all identified gaps in Chrome extension media detection

## Changes Made

### detector.js
1. **SPA navigation detection** - Added `popstate`, `hashchange` listeners + 2s URL polling interval to detect pushState/replaceState changes. Clears cooldowns and triggers rescan on route changes.
2. **Attribute mutation observation** - Added `attributes: true, attributeFilter: ['src', 'srcset', 'data', 'href', 'data-src', 'data-original-src']` to MutationObserver config. Catches in-place src swaps on lazy-loaded images and dynamic video players.
3. **Document extensions** - Added `pptx`, `xlsx`, `xps` to `_DOCUMENT_EXTENSIONS`. Added `presentation`/`spreadsheet` MIME type recognition in `_isDocumentUrl`.
4. **Shadow DOM traversal** - Added `_collectShadowRoots()` and `_querySelectorDeep()` helpers (depth-limited to 3, capped at 50 roots). Applied to `_scanImages`, `_scanAudioVideo`, `_scanDocuments`.
5. **Blob URL handling** - Images: allowed blob: URLs through `_addImageCandidate` (content script can fetch same-origin blobs). Audio/video: added `_resolveMediaSource()` to find real URLs from data attributes when MSE sets currentSrc to blob:. Added `_checkC2paHeaderLocal()` for in-page fetch of blob: URLs with bytes forwarded to service worker.
6. **CSS background-image scanning** - Added `_scanCssBackgroundImages()` targeting styled elements with `background` in inline style. Regex extracts https:// URLs from computed `background-image`. Capped at 200 elements, only runs on full-page scans.
7. **HLS/DASH streaming** - Added `_STREAMING_EXTENSIONS` set (`m3u8`, `mpd`). Scans `<a>` links to streaming manifests in `_scanDocuments`.
8. **Per-media-type bandwidth counters** - Split `_autoScanBytesUsed` into `_autoScanImageBytes`, `_autoScanMediaBytes`, `_autoScanDocumentBytes` with independent limits (10MB/10MB/5MB).
9. **Increased auto-scan caps** - Images: 20->50, Media: 10->20, Documents: 5->15.

### service-worker.js
- Added `CHECK_C2PA_BYTES` message handler: decodes base64 bytes and runs `_hasJumbfMarker()` analysis for blob: URLs that can't be fetched from the service worker context.

### Tests
- **detector.test.js**: Added tests for `_collectShadowRoots`, `_DOCUMENT_EXTENSIONS` (including new types), `_STREAMING_EXTENSIONS`, `_resolveMediaSource`, CSS background-image URL regex.
- **auto-scan-c2pa.test.js**: Updated for new function signature, per-type bandwidth counters, new scan limits.
- **image-verification.test.js**: Updated for new scan limits and per-type bandwidth references.
- All 413 tests pass.

## Status: COMPLETE

## Suggested Commit Message

```
feat(chrome-extension): close media detection gaps for v2.0.0

- SPA navigation: popstate/hashchange listeners + 2s URL poll for
  pushState detection, clears scan cooldowns on route change
- Attribute mutations: observe src/srcset/data-src changes on existing
  elements (lazy-loaded images, dynamic video players)
- Shadow DOM: recursive traversal of open shadow roots (depth 3,
  max 50 roots) for image/audio/video/document scanning
- Blob URL handling: content-script-side fetch for blob: images,
  data-attribute resolution for MSE video players, CHECK_C2PA_BYTES
  service worker handler for in-page byte analysis
- CSS background images: scan computed background-image for http URLs
  on styled elements (hero images, gallery cards)
- HLS/DASH: recognize .m3u8/.mpd streaming manifests in document scan
- Document extensions: add pptx, xlsx, xps to recognized formats
- Per-type bandwidth counters: independent 10MB/10MB/5MB limits for
  images, media, and documents prevent one category starving others
- Auto-scan caps: images 20->50, media 10->20, documents 5->15
```
