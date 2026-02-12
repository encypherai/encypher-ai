# TEAM_178 — WordPress Verification UI & Copy-Paste Fix

## Status: COMPLETE

## Issues Addressed
1. **Empty "View Full C2PA Manifest" dropdown** — FIXED. Removed the redundant `<details>` table that tried to render `claim_generator`/`instance_id`/`assertions` from the wrong metadata level. For `micro_ecc_c2pa` mode (sentence-level signing), the C2PA manifest is nested inside `metadata.manifest_data`, not at `metadata` top level. Added normalization logic to resolve the manifest from either location.
2. **Signer display** — FIXED. Now shows `signer_name` ("Demo Organization") instead of raw `signer_id` ("org_07dd7ff77fa7e949").
3. **Actions version** — FIXED. Now looks up `c2pa.actions.v2` first, then falls back to `v1`.

## Not Addressed (Out of Scope)
- **Copy-paste tampered issue** — When a user copies the entire WordPress page (nav, sidebar, footer included) into the external verify tool, the extra text causes a hash mismatch. This is an enterprise API / verification-service concern. The WordPress plugin's internal verify (badge click) works correctly because it extracts text from the stored HTML via `extract_text_for_verify()`.

## Changes Made
- `plugin/encypher-provenance/includes/class-encypher-provenance-frontend.php`
  - Removed empty "View Full C2PA Manifest" table dropdown
  - Added metadata normalization for micro_ecc_c2pa vs full C2PA modes
  - Show `signer_name` (preferred) or `signer_id` as fallback
  - Extract created timestamp from `c2pa.actions.v2` (then v1)
  - Display `softwareAgent` from the c2pa.created action
  - Show `document_id` from top-level or c2pa.metadata assertion
  - Show sentence/signature count when available
  - Added color-coded assertion chip summary
  - Improved error state UI with warning icon
  - JSON viewer collapsed by default with max-height

## Testing
- Puppeteer: Live API verification on post 84 (micro_ecc_c2pa) — all fields render correctly
- Puppeteer: Live API verification on post 61 (full C2PA with ingredients) — provenance chain shows "Edited — 2/12/2026, 3:31:21 PM" and "Created — 2/12/2026, 3:31:21 PM"
- PHP CLI: Verified metadata normalization resolves all 5 assertions, instance_id, claim_generator, document_id, total_signatures

## Git Commits
```
fix(wp-plugin): improve verification modal UI — remove empty manifest dropdown, normalize metadata
fix(wp-plugin): fix provenance chain timestamps and c2pa.edited fallback
```
