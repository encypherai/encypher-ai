# TEAM_288 - Chrome Extension SPA Compatibility and Authenticated Media

**Status**: COMPLETE

## Summary

Fixed three issues preventing the Chrome extension from working on SPA sites (Gemini, ChatGPT, etc.) and with authenticated media URLs.

## Changes

### 1. Credentialed media fetch (`service-worker.js`)
- Added `credentials: 'include'` to all media fetch calls: `verifyImage`, `verifyAudio`, `verifyVideo`, `verifyDocument`, and `_checkC2paHeader`
- This sends the user's session cookies when fetching media from authenticated CDNs (e.g. `contribution.usercontent.google.com` for Gemini videos)
- Extension's `<all_urls>` host permission grants cookie access for any domain

### 2. Content script disconnection handling (`popup.js`, `service-worker.js`)
- Added `RELAY_TO_TAB` message handler in service worker that wraps `sendFrameMessageWithFallback` (which re-injects content scripts on failure)
- Updated popup's `rescanPage()` to route RESCAN through the service worker relay instead of direct `chrome.tabs.sendMessage`
- Updated popup's `loadTabState()` inventory fetches (GET_PAGE_IMAGES, GET_PAGE_MEDIA, GET_PAGE_DOCUMENTS) to use the relay
- Eliminates "Unable to scan page" error on SPA sites where content script was disconnected by client-side navigation

### 3. `currentSrc` re-lookup bug (`detector.js`)
- Fixed `_autoScanImages` and `_autoScanMedia` to fall back to iterating all media elements and comparing `currentSrc`/`src` properties when the CSS `[src="..."]` selector fails
- The inventory stores `el.src || el.currentSrc`, but `currentSrc` is a computed property that doesn't appear in the HTML `src` attribute, so `[src="..."]` misses those elements

## Test Results
- 395/395 tests passing

## Commit Message Suggestion
```
fix(chrome-extension): SPA compatibility and authenticated media support

Add credentials to all media fetch calls so the extension can verify
media behind authenticated CDNs (Gemini, Google Workspace, etc.).

Route popup-to-content-script messages through the service worker's
sendFrameMessageWithFallback, which re-injects content scripts when
they become disconnected on SPA sites.

Fix element re-lookup in auto-scan to handle currentSrc differing
from the src HTML attribute.
```
