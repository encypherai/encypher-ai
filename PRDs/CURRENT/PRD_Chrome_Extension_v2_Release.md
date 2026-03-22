# Chrome Extension v2.0.0 Release Prep

## Status: COMPLETE

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

### 2.0 Chrome Web Store Listing Copy (DONE)
- [x] 2.0.1 Write short description (132 char max, shown in search results) -- 130 chars, in STORE_LISTING.md and manifest.json
- [x] 2.0.2 Write detailed description (full listing page) -- ~650 words in STORE_LISTING.md, follows marketing guidelines
- [x] 2.0.3 Write "What's New" text for the update (shown to existing users) -- 5 bullet points in STORE_LISTING.md
- [x] 2.0.4 Select category and tags for Web Store listing -- Productivity + News & Weather, 7 tags

### 3.0 Screenshots (1280x800 or 640x400) (DONE)
Chrome Web Store allows up to 5 screenshots. Each should have a clean, professional look with a brief caption overlay.

- [x] 3.0.1 Screenshot 1: Image verification badge on a news article page -- generated at 1280x800
  - File: store-assets/screenshot-1-image-verification.png
- [x] 3.0.2 Screenshot 2: Right-click context menu showing "Verify image with Encypher" -- generated at 1280x800
  - File: store-assets/screenshot-2-context-menu.png
- [x] 3.0.3 Screenshot 3: Popup showing "Media on page" section with verification results -- generated at 1280x800
  - File: store-assets/screenshot-3-popup-media.png
- [x] 3.0.4 Screenshot 4: Text verification badge on signed content -- generated at 1280x800
  - File: store-assets/screenshot-4-text-verification.png
- [x] 3.0.5 Screenshot 5: Options page with auto-scan toggle -- captured via Puppeteer at 1280x800
  - File: store-assets/screenshot-5-options-auto-scan.png

### 4.0 Promotional Assets (DONE)
- [x] 4.0.1 Small promotional tile (440x280) -- generated with v2.0 branding, media-type icons
  - File: store-assets/promo-tile-440x280.png
- [x] 4.0.2 Marquee promotional image (1280x800) -- generated with browser mockup and headline
  - File: store-assets/promo-marquee-1280x800.png

### 5.0 Release Notes (DONE)
- [x] 5.0.1 Write CHANGELOG entry for v2.0.0 -- CHANGELOG.md created with full version history
- [x] 5.0.2 Write internal release announcement -- docs/RELEASE_v2.0.0_INTERNAL.md

### 6.0 Pre-Publish Verification (DONE)
- [x] 6.0.1 Verify manifest.json is valid (version, description, permissions) -- all fields validated, description 130/132 chars
- [x] 6.0.2 Run full test suite: 378 unit tests pass + 19 E2E tests pass
- [x] 6.0.3 Manual smoke test -- skipped per user directive (automated tests sufficient: 378 unit + 19 E2E)
- [x] 6.0.4 Review permissions justification for Chrome Web Store review -- docs/PERMISSIONS_JUSTIFICATION.md created
- [x] 6.0.5 Package extension as .zip for Chrome Web Store upload -- dist/encypher-verify-2.0.0.zip

### Additional Fixes (discovered during release prep)
- [x] Fix package.json version: was 1.1.0, updated to 2.0.0
- [x] Fix options.html footer: was "v1.1.0", updated to "v2.0.0"
- [x] Fix manifest.json description: was 155 chars (over limit), shortened to 130 chars

---

## Success Criteria
- [x] Web Store listing accurately reflects v2.0.0 capabilities without overclaiming (Tier 1 only)
- [x] All 5 screenshots showcase new media verification features alongside existing text verification (5/5 complete)
- [x] Description copy follows Encypher marketing guidelines (tone, positioning, approved phrases)
- [x] No emoji, no Unicode decorations, ASCII only
- [x] "Verification is free" is prominently featured
- [x] C2PA standards authority is mentioned
- [x] All tests pass before packaging

## Completion Notes

### Completed by TEAM_271 (2026-03-22)

**Deliverables produced:**
1. `STORE_LISTING.md` -- Complete rewrite with v2.0.0 short description (130 chars), detailed description (~650 words), "What's New" (5 bullets), updated categories/tags, and full v2.0.0 version history entry.
2. `CHANGELOG.md` -- New file with structured changelog for all three versions (2.0.0, 1.1.0, 1.0.0).
3. `docs/RELEASE_v2.0.0_INTERNAL.md` -- Internal release announcement with feature summary, test coverage table, technical decisions, and next steps.
4. `docs/PERMISSIONS_JUSTIFICATION.md` -- Chrome Web Store permissions justification for all 5 permissions and host_permissions.
5. `dist/encypher-verify-2.0.0.zip` -- Packaged extension ready for Chrome Web Store upload.

**Screenshots (all 1280x800, in store-assets/):**
1. `screenshot-1-image-verification.png` -- News article with verified image badge overlay
2. `screenshot-2-context-menu.png` -- Right-click context menu with "Verify image with Encypher"
3. `screenshot-3-popup-media.png` -- Extension popup with Media on Page section
4. `screenshot-4-text-verification.png` -- Text verification badge with signer tooltip
5. `screenshot-5-options-auto-scan.png` -- Options page with auto-scan toggle (Puppeteer capture)

**Promotional assets (in store-assets/):**
1. `promo-tile-440x280.png` -- Small tile with v2.0 badge, media-type icons, tagline
2. `promo-marquee-1280x800.png` -- Marquee hero with browser mockup and C2PA positioning

**Bug fixes:**
- package.json version: 1.1.0 -> 2.0.0
- options.html footer: v1.1.0 -> v2.0.0
- manifest.json description: 155 chars -> 130 chars (within 132-char limit)

**Test results at time of packaging:**
- Unit tests: 378/378 pass
- E2E tests: 19/19 pass
