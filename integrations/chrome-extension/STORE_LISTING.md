# Chrome Web Store Listing - Encypher Verify

## Store Listing Information

### Name
Encypher Verify

### Short Description (132 characters max)
Verify provenance for any text, image, audio, or video on the web. Powered by C2PA -- cryptographic proof of origin, free for all.

### Detailed Description

**Verify Provenance Across Text, Images, Audio, and Video -- Free, No Account Required.**

Every day, content moves across the web without proof of who made it. Encypher Verify brings cryptographic provenance to your browser. Powered by the C2PA standard, it detects and verifies proof of origin in text, images, audio, and video on any website -- instantly, at no cost.

Version 2.0 expands far beyond text. Right-click any image, audio element, or video to verify its provenance. Automatic C2PA scanning detects signed images as you browse, with no action required. A new "Media on page" section in the popup shows every detected media element and its verification status at a glance.

**What you can verify:**

- Text: Detects invisible cryptographic watermarks (C2PA text manifests, zero-width character embeddings) on any webpage. Inline badges show verification status directly in the page.
- Images: Right-click any image to verify C2PA provenance. Automatic background scanning detects signed images via lightweight header inspection (first 4KB only). Verified images get a floating badge overlay.
- Audio: Right-click any audio element to verify. Supports files up to 50MB. No authentication required.
- Video: Right-click any video element to verify. Supports files up to 100MB. No authentication required.

**What you can sign:**

- Sign your own content directly in the browser with invisible cryptographic watermarks that survive copy-paste and distribution.
- Works inside Google Docs, ChatGPT, Claude, Gmail, Outlook Web, Slack, LinkedIn, GitHub, X/Twitter, Medium, and dozens of other editors.
- Choose your proof mode (Minimal, Embedded, or Compatible) and signing frequency (per document, paragraph, sentence, or section).
- Free tier includes 1,000 signings per month with a visual usage meter.

**Automatic C2PA image scanning:**

As you browse, Encypher Verify scans images on the page for C2PA provenance markers using lightweight Range requests that inspect only the first 4KB of each file. No full downloads. Built-in circuit breaker limits bandwidth to 10MB per page with a 5-minute cooldown, capping at 20 images and 3 concurrent requests. You can enable or disable auto-scanning in settings.

**How it works:**

1. For readers and fact-checkers: Browse normally. Encypher Verify automatically scans for provenance markers in text and images. When proof is present, you see verified status inline with signer identity and timestamp. Right-click any media element to verify on demand.

2. For authors: Get a free API key from dashboard.encypherai.com, configure it in settings, and use the Sign tab or inline editor buttons to embed cryptographic proof before publishing.

3. For publishers: Deploy proof of origin across your editorial workflow. Every article, image, and media asset can carry verifiable provenance that persists through distribution.

**Why Encypher Verify is different:**

Encypher is built on the C2PA standard -- the same open standard backed by Adobe, Google, BBC, OpenAI, and Microsoft. Encypher co-chairs the C2PA Text Provenance Task Force and authored Section A.7 of the specification, published January 8, 2026. This is not proprietary detection or statistical guessing. It is cryptographic proof embedded in content itself.

Verification is free for all media types. No account, no login, no cost. Signing is free at 1,000 operations per month.

**Privacy and security:**

- API key stored securely in local browser storage
- Only candidate content blocks are sent for verification, never full pages
- 1-hour local verification cache eliminates redundant API calls
- Anonymous discovery analytics (always on, no personal identifiers)
- Auto-scan inspects only image headers (4KB), not full file content

**Support:**

- Documentation: encypherai.com/docs
- Email: support@encypherai.com

### What's New in v2.0.0

- Image verification: Right-click any image to verify C2PA provenance. Verified images display a floating badge overlay.
- Audio and video verification: Right-click audio or video elements to verify provenance -- supports files up to 50MB (audio) and 100MB (video), no authentication required.
- Automatic C2PA image scanning: Lightweight header detection identifies signed images as you browse, with configurable toggle and built-in bandwidth limits.
- Media on page: New popup section shows all detected images, audio, and video on the current page with verification status and on-demand verify buttons.
- All verification is free -- no account required for any media type.

### Category
**Primary**: Productivity
**Secondary**: News & Weather

### Tags
C2PA, content authenticity, media provenance, verification, watermark detection, content verification, proof of origin

### Language
English

### Privacy Policy URL
https://encypherai.com/privacy

## Visual Assets

### Extension Icon (Required Sizes)

- **16x16**: `icons/icon16.png` [ready]
- **32x32**: `icons/icon32.png` [ready]
- **48x48**: `icons/icon48.png` [ready]
- **128x128**: `icons/icon128.png` [ready]

### Promotional Images (Required)

#### Small Promo Tile (440x280)
**Description**: Encypher Verify v2.0 -- "Text + Image + Audio + Video Verification" with brand colors
**File**: `store-assets/promo-small-440x280.png`
**Status**: Needs update for v2.0 (current tile is v1.x)

#### Large Promo Tile (920x680)
**Description**: Screenshot of extension verifying media across multiple types
**File**: `store-assets/promo-large-920x680.png`
**Status**: Needs update for v2.0

#### Marquee Promo Tile (1400x560)
**Description**: Hero image -- "Verify provenance for any content on the web" with multi-media showcase
**File**: `store-assets/promo-marquee-1400x560.png`
**Status**: Needs update for v2.0

### Screenshots (Required: 1-5 screenshots, 1280x800 or 640x400)

1. **Image Verification Badge**
   - Webpage with an image showing verified badge overlay at top-right
   - Caption: "Instantly verify image provenance on any website"
   - File: `store-assets/screenshot-1-image-verification-badge.png`

2. **Context Menu -- Media Verification**
   - Chrome context menu on an image with "Verify image with Encypher" option
   - Caption: "Right-click to verify any image, audio, or video"
   - File: `store-assets/screenshot-2-context-menu-media.png`

3. **Popup -- Media on Page**
   - Popup Verify tab with image/audio/video entries and verification statuses
   - Caption: "See all media on the page with verification status"
   - File: `store-assets/screenshot-3-popup-media-section.png`

4. **Text Verification Badge**
   - Paragraph with inline verification badge (existing feature)
   - Caption: "Detect cryptographic watermarks in text"
   - File: `store-assets/screenshot-4-text-verification-badge.png`

5. **Options -- Auto-Scan Toggle**
   - Settings page with "Auto-scan images for C2PA provenance" checkbox
   - Caption: "Automatic scanning -- configurable in settings"
   - File: `store-assets/screenshot-5-options-auto-scan.png`

**Status**: Screenshots need to be recaptured for v2.0 features

## Promotional Copy

### Tagline
"Verify provenance for any text, image, audio, or video on the web. Powered by C2PA -- cryptographic proof of origin, free for all."

### Key Benefits

1. **For Readers and Fact-Checkers**: Verify who made any text, image, audio, or video -- instantly, free.
2. **For Authors**: Sign your own content with invisible proof that survives copy-paste and distribution.
3. **For Publishers**: Deploy proof of origin across your full content portfolio -- articles, photos, podcasts, video.

### Use Cases

- **Journalism**: Verify news articles, photos, and video for proof of origin
- **Fact-Checking**: Confirm media provenance before sharing or citing
- **Academic**: Prove authorship of research, papers, and media assets
- **Creative**: Protect original writing, photography, audio, and video work
- **Legal**: Establish content provenance for evidentiary and compliance purposes
- **Marketing**: Verify brand-authorized content across media types

## Pricing

**Free Tier**: Unlimited verification across all media types (no API key required). 1,000 content signings per month with API key. All proof modes and frequency levels except per-word.
**Enterprise**: Unlimited verification and signing, per-word embedding frequency, Merkle tree verification, attribution tracking, fingerprinting. Contact sales at encypherai.com/contact.

## Support & Links

- **Website**: https://encypherai.com
- **Documentation**: https://encypherai.com/docs/chrome-extension
- **Support Email**: support@encypherai.com
- **Dashboard**: https://dashboard.encypherai.com

## Version History

### Version 2.0.0

**What's new:**
- Image verification via right-click context menu with floating badge overlay (verified/invalid/error) at image top-right
- Audio verification via right-click context menu -- Base64 POST to public /verify/audio endpoint (50MB limit, no auth)
- Video verification via right-click context menu -- multipart POST to public /verify/video endpoint (100MB limit, no auth)
- Automatic C2PA image scanning using lightweight Range-request header detection (first 4KB per image). Detects JUMBF markers in JPEG (APP11) and PNG (caBX). Configurable in settings with circuit breaker (10MB bandwidth limit per page, 5-min cooldown, max 20 images, max 3 concurrent)
- "Media on page" section in popup showing all detected images, audio, and video with verification status and on-demand verify buttons
- Auto-scan toggle in options page (default: enabled)
- All verification endpoints are public -- no authentication required for any media type

**Technical:**
- 378 unit tests + 19 E2E tests passing
- Manifest V3 with updated description
- Service worker handles image, audio, and video context menu actions
- Content script inventories page media and manages verification state per element
- MutationObserver support for dynamically loaded media on infinite-scroll pages
- Bandwidth-aware circuit breaker prevents excessive network usage during auto-scan

### Version 1.1.0

**What's new:**
- Native sign-button placement for ChatGPT, Claude, Gmail, Outlook Web, Slack, LinkedIn posts/messages/articles, GitHub issues/comments, X/Twitter, and Medium
- Upgraded inline signing UI with compact buttons, quick-sign flow, advanced options, signer identity cues, and verification follow-up links
- Improved editor detection across hosted editors, modal composers, and open shadow-root surfaces with floating fallback when a native toolbar anchor is unavailable
- Updated keyboard shortcut to `Alt+Shift+S`
- Stronger embedding-plan handling to preserve DOM/editor content more reliably before falling back to full text replacement

**Technical:**
- 160 automated tests passing
- Lint passing cleanly
- Production build strips localhost permissions for store upload

### Version 1.0.0 (Initial Release)

**Features:**
- Auto-detection of embedded proof-of-origin markers
- Inline verified authorship status with signer information
- Content signing with API key
- Configurable proof mode (Embedded / Compact) and embedding frequency (per sentence, paragraph, etc.)
- Context menu verification and signing
- Keyboard shortcut signing (Ctrl+Shift+E)
- WYSIWYG editor integration with floating sign buttons
- Options page for configuration
- Privacy-first design (no tracking)

**Technical:**
- Manifest V3
- Service worker architecture
- Secure API key storage
- 1-hour local verification cache
- 156 unit tests, E2E tested with Puppeteer
- Brand-consistent SVG icons (no emojis)
- Free/Enterprise tier support with usage tracking

## Submission Checklist

### Required Items

- [x] Extension package (.zip)
- [x] Detailed description (v2.0.0 updated)
- [x] Privacy policy
- [ ] Small promo tile (440x280) -- needs v2.0 update
- [ ] Screenshots (1280x800, 5 needed for v2.0)
- [x] Category selection (updated: Productivity + News & Weather)
- [x] Support email

### Optional Items

- [ ] Large promo tile (920x680) -- needs v2.0 update
- [ ] Marquee promo tile (1400x560) -- needs v2.0 update
- [ ] Video demo (YouTube link)

### Pre-Submission Testing

- [x] Test on clean Chrome profile
- [x] Verify all permissions are necessary
- [x] Test signing flow end-to-end
- [x] Test verification on multiple sites
- [ ] Test image/audio/video verification context menus
- [ ] Test auto-scan toggle in options
- [ ] Test popup media section rendering
- [x] Check all links in description
- [x] Spell check all copy

## Post-Launch

### Marketing

- [ ] Announce on Twitter/X
- [ ] Blog post on encypherai.com
- [ ] Submit to Product Hunt
- [ ] Share in C2PA community
- [ ] Email existing users about v2.0

### Monitoring

- [ ] Set up Chrome Web Store analytics
- [ ] Monitor user reviews
- [ ] Track installation metrics
- [ ] Collect user feedback on media verification

### Iteration

- [ ] Plan v2.1 features based on feedback
- [ ] Address any reported bugs
- [ ] Improve based on user requests
