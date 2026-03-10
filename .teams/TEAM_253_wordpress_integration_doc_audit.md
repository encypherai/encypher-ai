# TEAM_253 - WordPress Integration Doc Audit

## Objective
Audit http://localhost:3001/docs/wordpress-integration using Puppeteer against the live dev
WordPress install. Verify screenshots are accurate and instruction/feature copy is correct.

## Status
COMPLETE

## Bugs Found and Fixed

### 1. step3-api-key.png - Wrong screenshot (CRITICAL)
- Was: WordPress frontend "Sample Page" (public-facing page with verification badge)
- Should be: Encypher plugin Settings page showing Workspace Connection section
- Fix: Replaced with screenshot of http://localhost:8085/wp-admin/admin.php?page=encypher-settings
  showing Connection Health + Workspace Connection + email connect field

### 2. Step 6 used wrong image file (CRITICAL)
- Was: `![Signed post in WordPress](/assets/docs/wordpress/step4-options.png)` (duplicated Step 4 image)
- Should be: A screenshot showing the WordPress post editor with Encypher Provenance panel
- Fix: Created new asset `step6-signed-post.png` (post editor with "Signed with C2PA - Auto-updates on publish" visible in sidebar), updated page.tsx reference

### 3. Step 4 table used emoji (COPY)
- Was: checkmark emoji (violates ASCII-only project rule)
- Fix: Changed all "Yes" cells to plain "Yes"

### 4. Step 5 badge position labels wrong (COPY)
- Was: "Bottom of content", "Top of content", "Floating bottom-right"
- Actual plugin labels: "Bottom of post (above comments)", "Top of post", "Bottom-right corner (floating)"
- Fix: Updated to match actual plugin dropdown values

### 5. Step 5 Badge Appearance section described non-existent options (COPY)
- Was: "Style: Minimal, Standard, or Detailed" and "Theme: Auto, Light, or Dark"
- These options DO NOT EXIST in the actual plugin UI
- Fix: Replaced "Badge Appearance" section with "Badge Visibility" documenting the
  actual options: "Show C2PA badge" and "Whitelabeling"

## Screenshots Verified Accurate (no changes needed)
- step1-download.png - Integrations page with WordPress card (correct)
- step2-upload.png - WordPress Add Plugins upload screen (correct)
- step4-options.png - Plugin Signature Management + C2PA Settings (correct)
- step5-badge.png - Display Settings with badge position dropdown (correct)
- step6-bulk-sign.png (Step 7) - Bulk Sign page with "Successfully marked: 8 posts" (correct)
- step7-inventory.png (Step 9) - Content list with signed posts table (correct)

## Port 8085 vs Port 8888
Port 8085 ("Encypher Local") had CGJ/MVS ZWC characters rendering visibly in both the
Gutenberg editor and frontend (##, , & -, dashes appearing as visible glyphs). All
screenshots from port 8085 for Step 6 and Step 8 were retaken from port 8888 ("Encypher
WordPress Review Sandbox") which uses a different theme with correct invisible ZWC rendering.

Port 8888 differences:
- Clean content rendering (no ZWC artifacts)
- Encypher Provenance panel shows "Verified - Content authenticity confirmed" + sentence count
- frontend-badge.png now shows "Enterprise verified | ENTERPRISE" badge above Comments

## Files Changed
- apps/dashboard/public/assets/docs/wordpress/step3-api-key.png (replaced - correct WP admin page)
- apps/dashboard/public/assets/docs/wordpress/step6-signed-post.png (replaced - clean from port 8888)
- apps/dashboard/public/assets/docs/wordpress/frontend-badge.png (replaced - clean from port 8888)
- apps/dashboard/src/app/docs/wordpress-integration/page.tsx (copy + image ref fixes)

## Suggested Git Commit
```
fix(docs): correct WordPress integration guide screenshots and copy

- Replace step3-api-key.png: was showing WP frontend Sample Page, now shows
  Encypher plugin Settings page with Connection Health + Workspace Connection UI
- Replace step6-signed-post.png: retaken from clean install (port 8888), shows
  post editor with Encypher Provenance panel open ("Verified - Content authenticity
  confirmed", last signed, sentences protected, View C2PA Manifest)
- Replace frontend-badge.png: retaken from clean install (port 8888), shows signed
  post with Enterprise verified badge above Comments; previous screenshot had visible
  ZWC character artifacts from port 8085 CGJ/MVS font rendering issue
- Fix Step 6 image ref: was pointing to step4-options.png (duplicate), now uses
  step6-signed-post.png
- Fix Step 4 table: remove emoji checkmarks, use plain Yes (ASCII-only rule)
- Fix Step 5 badge position labels to match actual plugin dropdown values
- Fix Step 5: remove Badge Appearance section (Style/Theme options do not exist in
  the plugin); replace with Badge Visibility describing Show C2PA badge + Whitelabeling
```
