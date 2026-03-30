# TEAM_287 - Chrome Extension Comprehensive Media Type Support

## Status: COMPLETE

## Summary

Comprehensive update to the Chrome extension to detect and verify all media types supported by the Encypher API. Previously the extension only detected C2PA headers in JPEG and PNG images. Now it handles all 31+ MIME types across 6 media categories.

## Changes Made

### service-worker.js
- **Expanded `_hasJumbfMarker()`** from 2 format scanners to 9 format families:
  - ISO BMFF (`_scanIsoBmffForC2pa`) - covers AVIF, HEIC, HEIF, MP4, MOV, M4V, M4A
  - RIFF (`_scanRiffForC2pa`) - covers WebP, WAV, AVI
  - GIF (`_scanGifForC2pa`) - Application Extension blocks
  - PDF (`_scanPdfForC2pa`) - C2PA cross-reference markers
  - MP3/ID3 (`_scanId3ForC2pa`) - GEOB frame with JUMBF
  - EBML/TIFF/FLAC via `_scanBytesForJumbfSignature` fallback
- **Added `_C2PA_UUID` constant** for ISO BMFF uuid box matching
- **Expanded MIME maps**: `_guessMimeType` (5 -> 16 formats), `_guessAudioMimeType` (6 -> 11), `_guessVideoMimeType` (5 -> 10)
- **Added `_guessDocumentMimeType`** for PDF, EPUB, DOCX, ODT, OXPS
- **Added `_extFromMime`** unified extension-from-MIME helper, refactored `_videoExtFromMime` to use it
- **Added `mediaVerifyEndpoint`** to API_CONFIG (`/api/v1/verify/media`)
- **Added `verifyDocument()`** function using unified `/verify/media` endpoint with multipart/form-data
- **Updated `VERIFY_MEDIA` handler** to route `mediaType === 'document'` to `verifyDocument`
- **Added `verify-document-link` context menu** item for right-clicking document links
- **Added document link click handler** with tab state update and toast notification

### detector.js
- **Added document tracking state**: `_processedDocuments` Set, `_documentVerificationState` Map
- **Expanded `_scanImages()`** to detect `<picture>` elements with `<source srcset>` children
- **Added `_addImageCandidate()`** helper with dimension filtering (uses `<img>` child for `<picture>`)
- **Added `_firstSrcsetUrl()`** to extract first URL from srcset attribute
- **Added `_scanDocuments()`** - scans `<embed>`, `<object>`, `<iframe>` for document embeds
- **Added `_isDocumentUrl()`, `_addDocumentCandidate()`, `_urlExtension()`** helpers
- **Added `injectDocumentBadge()`** - badge overlay for document embeds
- **Added `_verifyDocumentAndBadge()`** - sends VERIFY_MEDIA with mediaType='document'
- **Wired `_scanDocuments()` into `scanPage()`** alongside image and AV scanning
- **Updated RESCAN handler** to clear document state and unwrap document badge wrappers
- **Added `VERIFY_DOCUMENT_CONTEXT` message handler**
- **Added `GET_PAGE_DOCUMENTS` message handler** for popup inventory
- **Updated `FOCUS_MEDIA` handler** to check `_documentVerificationState`

### popup.js
- **Updated `renderMediaSection()`** to accept and render `documentData` (third parameter)
- **Added document inventory rendering** with verify/locate buttons
- **Added `verifyDocumentFromPopup()`** function
- **Added `_mediaTypeLabel()`** helper - shows correct type label (Image/Audio/Video/Document)
- **Added `c2pa_document` to `markerTypeLabel()`**
- **Updated `isMedia` check** in renderDetails to include document types
- **Updated `loadTabState()`** to fetch `GET_PAGE_DOCUMENTS` and pass to render

### Tests
- **Updated `popup-verification-ux.test.js`** - regex pattern now includes `!hasDocuments`

## Commit Suggestion

```
feat(chrome-extension): comprehensive media type detection across all C2PA formats

Expand C2PA header detection from JPEG/PNG to all supported formats:
ISO BMFF (AVIF, HEIC, HEIF, MP4, MOV, M4V), RIFF (WebP, WAV, AVI),
GIF, PDF, MP3/ID3, EBML (WebM, MKV), TIFF/DNG, FLAC.

Add document verification via unified /verify/media endpoint for PDF,
EPUB, DOCX, ODT, OXPS embedded in pages. Expand DOM scanning to detect
<picture> elements, <embed>, <object>, and <iframe> document viewers.

Update popup to display document verification results with correct
media type labels. Add right-click context menu for document links.
All 378 existing tests pass.
```
