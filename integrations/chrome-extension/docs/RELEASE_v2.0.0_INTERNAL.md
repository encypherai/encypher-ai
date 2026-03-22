# Encypher Verify v2.0.0 -- Internal Release Announcement

**Date**: 2026-03-22
**Release Type**: Major version (1.1.0 -> 2.0.0)
**Status**: Ready for Chrome Web Store submission

---

## What Shipped

Encypher Verify v2.0.0 expands the Chrome extension from text-only verification to full-spectrum media provenance covering images, audio, and video. This is the first browser extension to offer C2PA-based verification across all four content types.

### New capabilities

- **Image verification**: Right-click context menu on any image. Floating badge overlay (verified/invalid/error) at image top-right. Automatic C2PA scanning via Range-request header detection (first 4KB per image).
- **Audio verification**: Right-click context menu on audio elements. Base64 POST to public /verify/audio. 50MB limit, no auth required.
- **Video verification**: Right-click context menu on video elements. Multipart POST to public /verify/video. 100MB limit, no auth required.
- **Auto-scan**: Lightweight background scanning detects signed images as users browse. JUMBF marker detection in JPEG (APP11) and PNG (caBX). Circuit breaker limits: 10MB bandwidth per page, 5-min cooldown, max 20 images, max 3 concurrent.
- **Media on page popup section**: Shows all detected images, audio, and video with status and on-demand verify buttons.
- **Options toggle**: Users can enable/disable auto-scan from settings.

### Unchanged capabilities

- Text verification (C2PA text manifests, ZWC embeddings)
- In-editor signing (Google Docs, ChatGPT, Claude, Gmail, Outlook, Slack, LinkedIn, GitHub, X, Medium)
- Badge overlays on verified/flagged text
- Context menu text verification and signing
- Keyboard shortcut signing (Alt+Shift+S)

## Test Coverage

| Category | Count | Status |
|----------|-------|--------|
| Unit tests (contract) | 378 | All passing |
| E2E tests (Puppeteer) | 19 | All passing |
| API integration tests | 15 | All passing |
| **Total** | **412** | **All passing** |

## Key Technical Decisions

- All media verification endpoints are public (no auth) -- aligns with the coalition principle that verification is free.
- Auto-scan uses Range requests (4KB only) rather than full image downloads to minimize bandwidth impact.
- Circuit breaker prevents runaway network usage on image-heavy pages.
- Audio uses Base64 encoding (simpler for smaller files); video uses multipart (necessary for larger files up to 100MB).

## Store Listing Updates Required

- Short description updated (132 chars, mentions all media types)
- Detailed description rewritten (~650 words, covers all new features)
- "What's New" text written (5 bullet points)
- Category updated to Productivity + News & Weather
- Tags added: C2PA, content authenticity, media provenance, verification, watermark detection
- CHANGELOG.md created with full version history

## Visual Assets Needed

- 5 new screenshots (specs in PRD tasks 3.0.1-3.0.5)
- Updated small promo tile (440x280) with v2.0 branding
- Updated marquee promo tile (1280x800) -- optional but recommended

## Related PRDs

- `PRDs/ARCHIVE/PRD_Image_Verification_Chrome.md` -- Image verification implementation
- `PRDs/ARCHIVE/PRD_Audio_Video_Verification.md` -- Audio/video verification implementation
- `PRDs/CURRENT/PRD_Chrome_Extension_v2_Release.md` -- This release prep

## Next Steps

1. Capture 5 screenshots with caption overlays (tasks 3.0.1-3.0.5)
2. Update promotional tiles with v2.0 branding (tasks 4.0.1-4.0.2)
3. Manual smoke test on clean Chrome profile (task 6.0.3)
4. Package .zip for Chrome Web Store upload (task 6.0.5)
5. Submit to Chrome Web Store review
