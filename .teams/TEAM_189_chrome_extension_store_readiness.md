# TEAM_189 — Chrome Extension Store Readiness & Dashboard Integration Docs

## Objective
Add documentation and installation/setup instructions to the dashboard Integrations tab for the Chrome extension, and ensure all extension assets are ready for Chrome Web Store release.

## Changes Made

### 1. Dashboard Integrations — Chrome Extension Card
- Created `ChromeExtensionCard.tsx` with two states: overview and setup guide
- Overview: shows card with "Available" badge, "Setup Guide" and "Install" buttons
- Setup guide: 4-step wizard (Install → Get API Key → Configure → Start using)
  - Step 1: Chrome Web Store link
  - Step 2: Link to dashboard API Keys page
  - Step 3: Instructions to paste API key in extension settings
  - Step 4: Feature overview grid (auto-detect, inline badges, sign from browser, right-click verify)
- Usage limits section (Free: 1k signings/month, Enterprise: unlimited)
- API Base URL display with copy button
- Added "Browser Extensions" section to `page.tsx` above "CMS Platforms"

### 2. manifest.json — Store Readiness
- Removed `http://localhost:8000/*` and `http://localhost:9000/*` from `host_permissions`
- Added `https://*.encypherai.com/*` for all Encypher subdomains
- Production-only host permissions now

### 3. README.md Updates
- Pro → Enterprise references
- Unicode symbols removed from badge states table
- Test count updated to 42
- Cache TTL updated to 1 hour
- Build instructions updated (no build step — zip source directly)
- Free tier limit documented

### 4. STORE_LISTING.md Updates
- Removed all emojis (✅ ⚠️)
- Added WYSIWYG editor support and usage tracking to features
- Updated pricing: Free (1k signings/month) + Enterprise
- Updated technical section: 42 tests, SVG icons, tier support
- Added 1-hour cache to privacy section

### 5. PRIVACY.md Updates
- Removed ❌ emoji bullets
- Updated cache TTL from 5 minutes to 1 hour throughout

### 6. SECURITY_CHECKLIST.md Updates
- Removed ✅ emojis from threat model (replaced with [x] checkboxes)
- Updated test count to 42
- Updated host_permissions reference (no more localhost)
- Marked completed deployment checklist items
- Updated audit status

## Files Changed
- `apps/dashboard/src/app/integrations/ChromeExtensionCard.tsx` — NEW: Chrome extension setup card
- `apps/dashboard/src/app/integrations/page.tsx` — Added Browser Extensions section with ChromeExtensionCard
- `integrations/chrome-extension/manifest.json` — Removed localhost host_permissions
- `integrations/chrome-extension/README.md` — Pro→Enterprise, test count, cache TTL, build instructions
- `integrations/chrome-extension/STORE_LISTING.md` — Emoji removal, pricing, features, asset status updated
- `integrations/chrome-extension/PRIVACY.md` — Emoji removal, cache TTL fix
- `integrations/chrome-extension/SECURITY_CHECKLIST.md` — Emoji removal, test count, deployment checklist
- `integrations/chrome-extension/scripts/generate-store-assets.js` — NEW: Puppeteer asset generator
- `integrations/chrome-extension/store-assets/` — NEW: 6 generated PNGs (3 screenshots, 3 promo tiles)

## Test Results
- **Dashboard**: `next build` passes clean
- **Chrome Extension**: 42/42 unit tests pass, 0 failures

### 7. Store Assets — Promo Images & Screenshots
- Created `scripts/generate-store-assets.js` Puppeteer script to render all assets from HTML templates
- All assets use brand colors (Deep Navy, Azure Blue, Light Sky Blue, Cyber Teal) and Google Fonts (Playfair Display, Roboto, Inter)
- **Screenshot 1** (`screenshot-1-verification-badges.png`, 1280x800): "The Encypher Times" article with Playfair Display masthead, two inline verification badges, floating tooltip showing "Verified Content / Signed by: The Encypher Times", Chrome browser bar with extension icon
- **Screenshot 2** (`screenshot-2-popup-interface.png`, 1280x800): Popup mockup with Verify/Sign tabs, 3 verified items (The Encypher Times, Reuters, AP), usage meter, Rescan button
- **Screenshot 3** (`screenshot-3-options-page.png`, 1280x800): Settings page with API key field, verification toggles, API Base URL, cache duration
- **Small Promo** (`promo-small-440x280.png`): Brand gradient background, logo mark, title, three feature pills (C2PA Standard, Free to Use, Privacy-First)
- **Large Promo** (`promo-large-920x680.png`): "Trust, Verified." headline, feature bullets with Cyber Teal dots, floating article card with verification badge
- **Marquee Promo** (`promo-marquee-1400x560.png`): "Verify Content. Build Trust." with Cyber Teal accent, "Add to Chrome — Free" CTA, three floating verification cards
- Updated STORE_LISTING.md: all submission checklist items marked complete

## Remaining Store Submission Items
- [ ] Test on Windows, Mac, Linux
- [ ] Update EXTENSION_ID_HERE in ChromeExtensionCard once published
- [ ] Update version number if needed before submission

## Suggested Git Commit Message
```
feat(dashboard,chrome-ext): add extension setup docs, store assets, release readiness

Dashboard:
- Add Chrome Extension card to Integrations page with 4-step setup guide
- New "Browser Extensions" section above CMS Platforms
- Usage limits, API Base URL display, feature overview grid

Chrome Extension Store Readiness:
- Remove localhost from manifest.json host_permissions
- Add https://*.encypherai.com/* wildcard
- Update README: Pro→Enterprise, 42 tests, 1hr cache, zip build instructions
- Update STORE_LISTING: remove emojis, free+enterprise pricing, WYSIWYG support
- Update PRIVACY: remove emojis, fix cache TTL to 1 hour
- Update SECURITY_CHECKLIST: remove emojis, 42 tests, deployment checklist

Store Assets (Puppeteer-generated):
- 3 screenshots (1280x800 @2x): article with badges+tooltip, popup, settings
- 3 promo tiles: small (440x280), large (920x680), marquee (1400x560)
- "The Encypher Times" example article with Playfair Display serif masthead
- All assets use brand colors and Google Fonts

Tests: dashboard builds clean, 42/42 extension tests pass
```
