# TEAM_234 — Chrome Extension Marketing & Launch

## Status: COMPLETE

## Objective
Chrome extension is live on Chrome Web Store. Update dashboard integrations card with real URL, create marketing tool page, and add CTAs across site.

## Changes

### 1. Dashboard — ChromeExtensionCard.tsx
- Fix placeholder Chrome Store URL to real: https://chromewebstore.google.com/detail/encypher-verify/pbmfpddbafkhdjemgcnegddmniflbjla
- Update badge from "Available" to "Live on Chrome Web Store"

### 2. Marketing site — /tools/chrome-extension (new page)
- Full product page following WordPress page pattern
- Hero, features, how-it-works, CTAs
- Free verification (no account), signing requires account
- Chrome Web Store install button

### 3. Marketing site — /config/tools.ts
- Add "Chrome Extension" entry pointing to /tools/chrome-extension

### 4. Marketing site — Sign/Verify tool pages + Try page
- Add CTA banner promoting Chrome extension
- "Verify on any webpage — install the free Chrome extension"

## Task List
- [x] Fix dashboard ChromeExtensionCard URL -- real store URL, badge updated to "Live on Chrome Web Store"
- [x] Create /tools/chrome-extension page -- full product page with hero, features, how-it-works, free/sign tiers, FAQ, CTA
- [x] Add to tools config -- appears in navbar Tools dropdown and /tools listing page
- [x] Add CTA to /try page -- "Verify on any webpage" banner with Chrome Web Store link
- [x] Add CTA to verify tool page -- inline banner after tool with direct install link
- [x] Add CTA to sign tool page -- inline banner linking to /tools/chrome-extension

## Suggested Commit Message
feat(marketing,dashboard): launch Chrome extension -- live store URL, new /tools/chrome-extension page, navbar entry, CTAs on sign/verify/try pages

- Update ChromeExtensionCard with real Chrome Web Store URL and "Live" badge
- Add /tools/chrome-extension marketing page (hero, features, free/sign tiers, FAQ)
- Register in tools config so it appears in navbar dropdown and /tools listing
- Add extension CTAs on /try, /tools/verify, and /tools/sign pages
