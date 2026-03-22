# Chrome Extension v2.0.0 Release Prep

## Status: NOT STARTED

## Current Goal
Prepare all Chrome Web Store assets, listing copy, screenshots, and release notes for the v2.0.0 major release of Encypher Verify.

## Overview
The Chrome extension has expanded from text-only verification to full-spectrum media provenance: images, audio, video, and automatic C2PA scanning. This is a major version bump (1.1.0 -> 2.0.0) that requires updated Web Store listing copy, screenshots, promotional assets, and release notes. The manifest version and description have already been bumped.

## What Changed in v2.0.0

### New Capabilities
- **Image verification**: Right-click any image -> "Verify image with Encypher" context menu. Floating badge overlay (verified/invalid/error) at image top-right.
- **Audio verification**: Right-click any audio element -> verify. Base64 POST to public /verify/audio (50MB limit, no auth).
- **Video verification**: Right-click any video element -> verify. Multipart POST to public /verify/video (100MB limit, no auth).
- **Automatic C2PA image scanning**: Lightweight Range-request header detection (first 4KB of each image). Scans for JUMBF markers in JPEG (APP11) and PNG (caBX). Configurable in options (default: enabled). Circuit breaker (10MB bandwidth limit per page, 5-min cooldown, max 20 images, max 3 concurrent).
- **Media section in popup**: "Media on page" shows all detected images, audio, and video with verification status and "Verify" buttons.
- **Auto-scan toggle in options**: Users can enable/disable automatic C2PA image scanning.

### Existing Capabilities (unchanged)
- Text verification: Detects Unicode steganographic watermarks (C2PA text manifests, ZWC embeddings) on any webpage
- In-editor signing: Sign content directly in Google Docs, Microsoft Word Online, and other rich text editors
- Badge overlays on verified/flagged text content
- Context menu text verification

---

## Messaging Guidelines

### Positioning
- **Standards authority**: Encypher co-chairs the C2PA Text Provenance Task Force (published January 8, 2026)
- **Tier 1 detection only**: The extension verifies provenance in content on the open web. Do NOT imply it detects AI ingestion (Tier 2) or AI output sourcing (Tier 3).
- **"Verification is free"**: No auth, no cost, all media types. This is a coalition principle.
- **Collaborative, not adversarial**: "Building WITH the AI industry through C2PA"
- **Cryptographic certainty**: "Proof of origin -- mathematical certainty, not statistical guessing"

### Target Audience for Web Store
Journalists, researchers, content creators, fact-checkers, publishers, and technically-curious users. Frame as "verify before you share" and "see who really made this" -- not legal/licensing language.

### Approved Phrases
- "Cryptographic proof of origin"
- "Powered by the C2PA standard"
- "Verify any text, image, audio, or video"
- "Proof embedded in content itself"
- "Free verification -- no account required"
- "Works on any website"
- "Automatic C2PA detection as you browse"

### Phrases to Avoid
- Emoji or Unicode decorations (ASCII only)
- "AI companies have no choice"
- "Comply or continue litigation"
- Any Tier 2/3 claims ("detects AI ingestion", "traces AI training data")
- "Court-admissible" without qualification
- "The only solution"

---

## Tasks

### 1.0 Manifest and Version (DONE)
- [x] 1.0.1 Bump version from 1.1.0 to 2.0.0
- [x] 1.0.2 Update manifest description to reflect multi-media capabilities

### 2.0 Chrome Web Store Listing Copy
- [ ] 2.0.1 Write short description (132 char max, shown in search results)
  - Current: "Verify who authored any text on the web. Sign your own content with invisible cryptographic watermarks that survive copy-paste."
  - Needs to mention image/audio/video verification
- [ ] 2.0.2 Write detailed description (full listing page)
  - Structure: hero value prop -> what's new in v2 -> feature list -> how it works -> who it's for -> standards credibility
  - Include: text verification, image/audio/video verification, auto-scan, in-editor signing
  - Include: "Free -- no account required to verify" prominently
  - Include: C2PA standards authority positioning
  - Word count: 500-800 words
  - Reference: docs/company_internal_strategy/Encypher_Marketing_Guidelines.md for tone
- [ ] 2.0.3 Write "What's New" text for the update (shown to existing users)
  - 3-5 bullet points highlighting major additions
  - Keep it concise -- users scan this quickly
- [ ] 2.0.4 Select category and tags for Web Store listing
  - Suggested categories: Productivity, News & Weather
  - Tags: C2PA, content authenticity, media provenance, verification, watermark detection

### 3.0 Screenshots (1280x800 or 640x400)
Chrome Web Store allows up to 5 screenshots. Each should have a clean, professional look with a brief caption overlay.

- [ ] 3.0.1 Screenshot 1: Image verification badge on a real news article page
  - Show a webpage with an image that has a verified badge overlay at top-right
  - Caption: "Instantly verify image provenance on any website"
- [ ] 3.0.2 Screenshot 2: Right-click context menu showing "Verify image with Encypher"
  - Show Chrome's context menu on an image with the Encypher verify option
  - Caption: "Right-click to verify any image, audio, or video"
- [ ] 3.0.3 Screenshot 3: Popup showing "Media on page" section with verification results
  - Show the popup Verify tab with image/audio/video entries and verification statuses
  - Caption: "See all media on the page with verification status"
- [ ] 3.0.4 Screenshot 4: Text verification badge on signed content
  - Show a paragraph with an inline verification badge (existing feature, still important to showcase)
  - Caption: "Detect cryptographic watermarks in text"
- [ ] 3.0.5 Screenshot 5: Options page with auto-scan toggle
  - Show the settings page with the "Auto-scan images for C2PA provenance" checkbox
  - Caption: "Automatic scanning -- configurable in settings"

### 4.0 Promotional Assets
- [ ] 4.0.1 Small promotional tile (440x280)
  - Clean design with Encypher logo, "v2.0" badge, and "Text + Image + Audio + Video Verification" tagline
  - Use brand colors from marketing site
- [ ] 4.0.2 Marquee promotional image (1280x800) -- optional but recommended
  - Hero image showing the extension in action across multiple media types
  - Tagline: "Verify provenance for any content on the web"

### 5.0 Release Notes
- [ ] 5.0.1 Write CHANGELOG entry for v2.0.0
  - Include all new features with brief descriptions
  - Note: "Verification is free for all media types -- no account required"
  - Note: API endpoints for audio/video verification are now public
- [ ] 5.0.2 Write internal release announcement (for team/stakeholders)
  - Summary of what shipped, test coverage (378 contract + 19 E2E + 15 API integration)
  - Link to archived PRDs

### 6.0 Pre-Publish Verification
- [ ] 6.0.1 Verify manifest.json is valid (version, description, permissions)
- [ ] 6.0.2 Run full test suite: `npm test && xvfb-run --auto-servernum npm run test:e2e`
- [ ] 6.0.3 Manual smoke test: load unpacked extension in Chrome, verify image/audio/video context menus appear, verify popup media section renders
- [ ] 6.0.4 Review permissions justification for Chrome Web Store review
  - `<all_urls>` host_permissions: required to fetch image/audio/video bytes with C2PA metadata intact from any domain
  - `contextMenus`: required for right-click verify on media elements
  - `storage`: required for user settings (API key, auto-scan toggle)
- [ ] 6.0.5 Package extension as .zip for Chrome Web Store upload

---

## Success Criteria
- Web Store listing accurately reflects v2.0.0 capabilities without overclaiming (Tier 1 only)
- All 5 screenshots showcase new media verification features alongside existing text verification
- Description copy follows Encypher marketing guidelines (tone, positioning, approved phrases)
- No emoji, no Unicode decorations, ASCII only
- "Verification is free" is prominently featured
- C2PA standards authority is mentioned
- All tests pass before packaging

## Completion Notes
(To be filled upon completion)
