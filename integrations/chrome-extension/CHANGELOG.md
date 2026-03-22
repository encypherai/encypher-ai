# Changelog

All notable changes to Encypher Verify are documented in this file.

## [2.0.0] - 2026-03-22

### Added

- **Image verification**: Right-click any image and select "Verify image with Encypher." Verified images display a floating badge overlay (verified/invalid/error) at the top-right corner of the image.
- **Audio verification**: Right-click any audio element to verify provenance. Uses Base64 POST to the public /verify/audio endpoint. Supports files up to 50MB. No authentication required.
- **Video verification**: Right-click any video element to verify provenance. Uses multipart POST to the public /verify/video endpoint. Supports files up to 100MB. No authentication required.
- **Automatic C2PA image scanning**: Lightweight Range-request header detection inspects the first 4KB of each image for JUMBF markers in JPEG (APP11) and PNG (caBX). Enabled by default. Configurable in options. Circuit breaker: 10MB bandwidth limit per page, 5-minute cooldown, max 20 images, max 3 concurrent requests.
- **Media on page popup section**: The Verify tab now includes a "Media on page" section showing all detected images, audio, and video elements with verification status and on-demand "Verify" buttons.
- **Auto-scan toggle in options**: Users can enable or disable automatic C2PA image scanning from the settings page.
- **Context menu entries**: New "Verify image with Encypher", "Verify audio with Encypher", and "Verify video with Encypher" context menu items for their respective media types.
- **Media focus**: "Locate" button on verified audio/video items in the popup scrolls to and highlights the element on the page.

### Changed

- Manifest description updated to reflect multi-media capabilities.
- Popup Verify tab now shows combined text and media verification results.
- Service worker handles image, audio, and video verification dispatching alongside text.
- Content detector now inventories page images, audio, and video elements and manages per-element verification state.
- MutationObserver extended to detect dynamically loaded media on infinite-scroll pages.

### Technical

- 378 unit tests + 19 E2E tests + 15 API integration tests passing.
- Version bumped from 1.1.0 to 2.0.0 in manifest.json, package.json, and options page.
- Verification is free for all media types -- no account required.
- All media verification endpoints are public (no auth).

## [1.1.0] - 2026-02-15

### Added

- Native sign-button placement for ChatGPT, Claude, Gmail, Outlook Web, Slack, LinkedIn posts/messages/articles, GitHub issues/comments, X/Twitter, and Medium.
- Upgraded inline signing UI with compact buttons, quick-sign flow, advanced options, signer identity cues, and verification follow-up links.
- Keyboard shortcut updated to Alt+Shift+S.

### Changed

- Improved editor detection across hosted editors, modal composers, and open shadow-root surfaces with floating fallback.
- Stronger embedding-plan handling to preserve DOM/editor content more reliably.

### Technical

- 160 automated tests passing.
- Lint passing cleanly.
- Production build strips localhost permissions for store upload.

## [1.0.0] - 2026-01-15

### Added

- Auto-detection of embedded proof-of-origin markers.
- Inline verified authorship status with signer information.
- Content signing with API key.
- Configurable proof mode (Embedded / Compact) and embedding frequency.
- Context menu verification and signing.
- Keyboard shortcut signing (Ctrl+Shift+E).
- WYSIWYG editor integration with floating sign buttons.
- Options page for configuration.
- Privacy-first design (no tracking).

### Technical

- Manifest V3 with service worker architecture.
- Secure API key storage.
- 1-hour local verification cache.
- 156 unit tests, E2E tested with Puppeteer.
- Brand-consistent SVG icons.
- Free/Enterprise tier support with usage tracking.
