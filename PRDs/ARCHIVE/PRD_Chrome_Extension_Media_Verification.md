# Chrome Extension Media Verification

## Status: COMPLETE

## Current Goal
All three phases complete with full test coverage (378 contract + 19 E2E). Ready for ARCHIVE.

## Overview
The Encypher Chrome extension detects and verifies invisible Unicode steganography (C2PA text manifests, ZWC embeddings) in web page text. The enterprise API already supports verification of binary media -- images (public), audio and video (currently Enterprise-gated, ungating tracked in PRD_API_Ungate_Media_Verification.md) -- via C2PA JUMBF manifest extraction. The extension has no code path for media assets. This PRD bridges that gap in three phases: image verification first (public API, broadest use case), then audio/video (public after API ungating), then automatic C2PA scanning.

## Objectives
- Enable on-demand verification of images on any web page via context menu and popup
- Display C2PA provenance badges on verified images inline on the page
- Support audio and video verification for all users (pending API ungating -- see PRD_API_Ungate_Media_Verification.md)
- Automatically detect and verify C2PA-signed images without user action
- Maintain the existing text verification UX -- media verification is additive, not a replacement
- Keep permission escalation minimal and justified for Chrome Web Store review

---

## Architecture Decisions

### AD-1: How to fetch image bytes from the extension

**Decision**: Service worker fetch with `<all_urls>` host_permissions

**Options considered**:

| Option | Pros | Cons |
|--------|------|------|
| A. Service worker fetch + `<all_urls>` host_permissions | Simple, no CORS issues, works for any public image | Permission escalation (but extension already runs content scripts on `<all_urls>`) |
| B. Server-side URL proxy endpoint | No permission escalation | New API endpoint, extra latency, won't work for auth-gated images |
| C. Content script fetch | No permission change needed | CORS blocks cross-origin images (most CDN-hosted images) |
| D. Canvas extraction | Works same-origin | Loses JUMBF metadata (canvas gives pixel data, not raw file bytes) |

**Rationale**: Option A is the only approach that reliably retrieves the original file bytes (with C2PA JUMBF metadata intact) for arbitrary images. The extension already declares `<all_urls>` in content_scripts matches, so the incremental permission ask is defensible in Chrome Web Store review. Options C and D have fundamental technical blockers. Option B adds API surface area and latency for marginal permission benefit.

### AD-2: When to verify images

**Decision**: Phase 1 is on-demand only (context menu + popup). Phase 3 adds automatic scanning.

**Rationale**: Verifying every image on every page would be bandwidth-intensive and quota-consuming. On-demand verification lets users choose what to verify. Automatic scanning in Phase 3 uses a lightweight JUMBF header check (Range request for first 4KB) to avoid downloading full images unnecessarily.

### AD-3: Tier gating for media types

**Decision**: All media verification is public (no auth). Media signing remains Enterprise-gated.

**Rationale**: Company strategy principle: "Verification is free because verifiability is the point." Gating verification undermines the value of Enterprise customers' signed media -- if third parties can't verify, signing has no value. Audio/video verification endpoints need API-side ungating first (see PRD_API_Ungate_Media_Verification.md).

| Media Type | API Endpoint (target) | Auth Required | Extension Tier Gate |
|------------|----------------------|---------------|---------------------|
| Image | `POST /verify/image` | No (public, already live) | None -- all users |
| Audio | `POST /verify/audio` (new, post-ungating) | No (public) | None -- all users |
| Video | `POST /verify/video` (new, post-ungating) | No (public) | None -- all users |

**Dependency**: Phase 2 (audio/video) is blocked on PRD_API_Ungate_Media_Verification.md completing first.

### AD-4: Badge placement for media elements

**Decision**: Floating overlay badge positioned at top-right corner of the media element, using the existing `_positionFloatingBadge` pattern from editor-signer.js.

**Rationale**: Appending inside `<img>` is not possible (void element). Absolute-positioned overlay within a wrapper or relative to the nearest positioned ancestor follows the existing floating badge pattern used for editable content.

---

## Tasks

### Phase 1: Image Verification (On-Demand)

#### 1.0 Manifest and Permissions
- [x] 1.0.1 Add `<all_urls>` to `host_permissions` in manifest.json -- 248/248 tests pass
- [x] 1.0.2 Add `VERIFY_MEDIA` and `VERIFY_IMAGE_CONTEXT` message types -- 248/248 tests pass
- [x] 1.0.3 Add image verify endpoint to `API_CONFIG` (`/api/v1/verify/image`) -- 248/248 tests pass

#### 1.1 Service Worker: Image Verification Handler
- [x] 1.1.1 Add `verifyImage(imageUrl)` function in service-worker.js -- 248/248 tests pass
- [x] 1.1.2 Add `VERIFY_MEDIA` message handler in `onMessage` listener -- 248/248 tests pass
- [x] 1.1.3 Image verification cache (reuses existing verificationCache, keyed by URL hash, 5-min TTL) -- 248/248 tests pass
- [x] 1.1.4 In-flight deduplication (reuses existing verificationInFlight) -- 248/248 tests pass
- [x] 1.1.5 TabState updated via existing updateTabStateWithVerification (no separate media counters needed) -- 248/248 tests pass
- [x] 1.1.6 VerificationDetail extended with `contentType` and `mediaUrl` fields -- 248/248 tests pass
- [x] 1.1.7 getIconStateForTab works unchanged (media results use same valid/invalid/revoked states) -- 248/248 tests pass

#### 1.2 Service Worker: Verification Utils
- [x] 1.2.1 Media detail built via existing `buildVerificationDetail` + contentType/mediaUrl decoration -- 248/248 tests pass
- [x] 1.2.2 Image verify response normalization handled inline in verifyImage() -- 248/248 tests pass

#### 1.3 Content Script: Image Detection and Badge Injection
- [x] 1.3.1 Add `_scanImages(root)` function in detector.js -- 248/248 tests pass
- [x] 1.3.2 Add `injectImageBadge(imgElement, status, details)` with wrapper pattern -- 248/248 tests pass
- [x] 1.3.3 Integrate `_scanImages()` into `scanPage()` pipeline (inventory-only) -- 248/248 tests pass
- [x] 1.3.4 Add `VERIFY_IMAGE_CONTEXT` message handler + `_verifyImageAndBadge` flow -- 248/248 tests pass
- [x] 1.3.5 Add `FOCUS_MEDIA` message handler -- 248/248 tests pass
- [x] 1.3.6 MutationObserver: existing childList observer already feeds scanPage with lazy-loaded images; attribute observer deferred to Phase 3

#### 1.4 Context Menu: Image Verification
- [x] 1.4.1 Register `verify-image` context menu item with `contexts: ['image']` -- 248/248 tests pass
- [x] 1.4.2 Handle `verify-image` click: extract `info.srcUrl`, send to content script -- 248/248 tests pass
- [x] 1.4.3 Pending badge shown via `_verifyImageAndBadge` before API call -- 248/248 tests pass

#### 1.5 Popup: Image Verification UI
- [x] 1.5.1 Add "Images on page" media section to Verify tab -- 248/248 tests pass
- [x] 1.5.2 Media detail rendering with `contentType` discriminator + locate-on-page -- 248/248 tests pass
- [x] 1.5.3 loadTabState fetches GET_PAGE_IMAGES inventory -- 248/248 tests pass

#### 1.6 CSS: Image Badge Styles
- [x] 1.6.1 `.encypher-image-badge-wrapper` with position:relative -- 248/248 tests pass
- [x] 1.6.2 `.encypher-badge--media` compact variant (24x24, positioned top-right) -- 248/248 tests pass
- [x] 1.6.3 Media badge tooltip positioning -- 248/248 tests pass

#### 1.7 Testing: Phase 1
- [x] 1.7.1-1.7.4 49 contract tests covering: manifest, service worker, detector, badge CSS, popup -- 248/248 tests pass
- [x] 1.7.5 Puppeteer E2E: no false-positive badges on non-C2PA images -- 19/19 E2E tests pass
- [x] 1.7.6 Puppeteer E2E: popup shows "Media on page" section when images present -- 19/19 E2E tests pass
- [x] 1.7.7 Puppeteer E2E: image detection on media test page -- 19/19 E2E tests pass

### Phase 2: Audio and Video Verification (Public)

**Dependency**: PRD_API_Ungate_Media_Verification.md COMPLETE -- public `/verify/audio` and `/verify/video` endpoints live.

#### 2.0 API Configuration
- [x] 2.0.1 Add audio/video verify endpoints to `API_CONFIG` -- 378/378 tests pass

#### 2.1 Service Worker: Audio/Video Handlers
- [x] 2.1.1 Add `verifyAudio(audioUrl)` function (base64 POST, 50MB limit, cache+dedup) -- 378/378 tests pass
- [x] 2.1.2 Add `verifyVideo(videoUrl)` function (multipart FormData, 50MB limit, cache+dedup) -- 378/378 tests pass
- [x] 2.1.3 Extend `VERIFY_MEDIA` handler to route by `mediaType: 'audio' | 'video'` with c2pa_audio/c2pa_video markerTypes -- 378/378 tests pass
- [x] 2.1.4 Detail building handled inline in verifyAudio/verifyVideo (same pattern as verifyImage) -- 378/378 tests pass

#### 2.2 Content Script: Audio/Video Detection
- [x] 2.2.1 Add `_scanAudioVideo(root)` function -- queries audio/video elements, extracts from <source> children, skips data:/blob: URIs -- 378/378 tests pass
- [x] 2.2.2 Add `injectMediaBadge()` and `_verifyMediaAndBadge()` for audio/video badge injection -- 378/378 tests pass
- [x] 2.2.3 Integrate `_scanAudioVideo()` into `scanPage()` pipeline -- 378/378 tests pass

#### 2.3 Context Menu: Audio/Video
- [x] 2.3.1 Register `verify-audio` context menu item (`contexts: ['audio']`) -- 378/378 tests pass
- [x] 2.3.2 Register `verify-video` context menu item (`contexts: ['video']`) -- 378/378 tests pass
- [x] 2.3.3 Handle context menu clicks via VERIFY_AUDIO_CONTEXT/VERIFY_VIDEO_CONTEXT -- 378/378 tests pass

#### 2.4 Popup: Audio/Video UI
- [x] 2.4.1 Extend Media section with audio/video entries (GET_PAGE_MEDIA, verifyMediaFromPopup) -- 378/378 tests pass
- [x] 2.4.2 Show audio/video verification results with contentType discriminator -- 378/378 tests pass

#### 2.5 Testing: Phase 2
- [x] 2.5.1 49 contract tests for audio/video (audio-video-verification.test.js) -- 378/378 tests pass
- [x] 2.5.2 Puppeteer E2E: data: URI audio/video skipped (no false badges) -- 19/19 E2E tests pass
- [x] 2.5.3 Puppeteer E2E: media test page loads without errors -- 19/19 E2E tests pass
- [x] 2.5.4 Puppeteer E2E: oversized video error path covered by contract tests (service worker 50MB check)

### Phase 3: Automatic C2PA Image Scanning

#### 3.0 Lightweight C2PA Detection
- [x] 3.0.1 Add `_checkC2paHeader(imageUrl)` -- detector delegates via CHECK_C2PA_HEADER to service worker; service worker does Range request for first 4KB, calls `_hasJumbfMarker()` -- 378/378 tests pass
- [x] 3.0.2 Add JPEG/PNG header parsing in service worker -- `_hasJumbfMarker()`, `_scanJpegForC2pa()` (APP11 0xEB + jumb/jumd), `_scanPngForC2pa()` (caBX chunk) -- 378/378 tests pass
- [x] 3.0.3 Add configurable scan limit (AUTO_SCAN_MAX_IMAGES = 20) -- 378/378 tests pass

#### 3.1 Auto-Scan Pipeline
- [x] 3.1.1 Add `_autoScanImages()` with requestIdleCallback, concurrency limit (AUTO_SCAN_MAX_CONCURRENT = 3) -- 378/378 tests pass
- [x] 3.1.2 Auto-verify images where `_checkC2paHeader()` returns true via `_verifyImageAndBadge()` -- 378/378 tests pass
- [x] 3.1.3 Add `autoScanImages` setting (default: true) checked before scanning -- 378/378 tests pass
- [x] 3.1.4 Update options page with auto-scan toggle (checkbox + label) -- 378/378 tests pass

#### 3.2 Performance and Bandwidth
- [x] 3.2.1 Add bandwidth tracking (`_autoScanBytesUsed`, 4096 per check) -- 378/378 tests pass
- [x] 3.2.2 Add circuit breaker (AUTO_SCAN_BANDWIDTH_LIMIT = 10MB) -- 378/378 tests pass
- [x] 3.2.3 Add scan cooldown (AUTO_SCAN_COOLDOWN_MS = 5 min) with `_autoScanPageCooldown` map -- 378/378 tests pass
- [x] 3.2.4 Skip images already in `_imageVerificationState` cache -- 378/378 tests pass

#### 3.3 Testing: Phase 3
- [x] 3.3.1 32 contract tests for C2PA header detection, JUMBF parsing, auto-scan pipeline, bandwidth/circuit breaker, options toggle (auto-scan-c2pa.test.js) -- 378/378 tests pass
- [x] 3.3.2 Circuit breaker and rate limiting covered in contract tests -- 378/378 tests pass
- [x] 3.3.3 Puppeteer E2E: auto-scan toggle present, checked by default, toggleable -- 19/19 E2E tests pass
- [x] 3.3.4 Puppeteer E2E: non-C2PA images stay responsive, no false positives -- 19/19 E2E tests pass
- [x] 3.3.5 Puppeteer E2E: auto-scan label describes C2PA provenance purpose -- 19/19 E2E tests pass

---

## Success Criteria

### Phase 1
- User can right-click any image on a web page and verify it via context menu
- Verified images display a provenance badge overlay (verified/invalid/error states)
- Popup shows image count and verification results alongside text results
- "Locate on page" works for image results
- No regression in text verification functionality
- All unit and Puppeteer E2E tests pass

### Phase 2
- Any user can verify audio and video elements via context menu (public endpoints)
- Audio/video verification results appear in popup alongside image and text results
- Video files > 50MB are rejected with a clear error message
- No tier gating in the extension -- verification is free for all media types

### Phase 3
- C2PA-signed images are automatically detected and verified on page load
- Non-C2PA images are not downloaded or sent to the API
- Auto-scan setting is configurable in extension options
- Page performance is not degraded (circuit breaker, rate limiting, idle callbacks)
- Bandwidth usage is bounded (< 10MB per page for scanning)

## Completion Notes

All three phases implemented and fully tested:
- 378 contract tests (0 regression)
- 19 Puppeteer E2E tests (9 new media + 10 existing, 0 regression)

**Phase 1** (TEAM_270): On-demand image verification via context menu and popup. 49 contract tests + 3 E2E tests.
**Phase 2** (TEAM_270): Audio/video verification with base64 (audio) and multipart (video) upload patterns, context menus, popup UI. 49 contract tests + 2 E2E tests.
**Phase 3** (TEAM_270): Automatic C2PA image scanning with Range-request header detection, JUMBF marker parsing (JPEG APP11 + PNG caBX), concurrency limits, bandwidth circuit breaker, cooldown, and options toggle. 32 contract tests + 4 E2E tests.

E2E tests require xvfb for headless CI: `xvfb-run --auto-servernum node --test tests/e2e/*.test.js`
