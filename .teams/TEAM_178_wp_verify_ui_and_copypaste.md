# TEAM_178 — WordPress Verification UI & Copy-Paste Fix

## Status: IN PROGRESS

## Issues
1. **Empty "View Full C2PA Manifest" dropdown** — The first `<details>` section in the verification modal tries to render `data.metadata.claim_generator` and `data.metadata.instance_id`, but the verify response puts those inside `data.metadata.manifest` (nested). The table renders empty. Also, it's redundant with the "View Complete C2PA Manifest (JSON)" section below.
2. **Tampered on full-page copy-paste** — When a user copies the entire WordPress page (including admin bar, nav, sidebar, footer) and pastes into the marketing site verify tool, the extra non-signed text causes a hash mismatch → "tampered". The C2PA content hash only covers the article body text.
3. **No verified text display** — The verification modal doesn't show what text was actually verified.

## Plan
- Fix 1: Remove the empty "View Full C2PA Manifest" table dropdown. Replace with a cleaner summary showing signer_name, created timestamp, document_id, and sentence count from the manifest assertions.
- Fix 2: The `signer_name` field is already returned by the API but the frontend only shows `signer_id`. Display `signer_name` when available.
- Fix 3: Also look up `c2pa.actions.v2` (not just `v1`) for the created timestamp.
- The copy-paste tampered issue is an enterprise API / verification-service concern — the WordPress plugin's internal verify (badge click) works correctly because it extracts text from the stored HTML. The external verify tool issue is out of scope for this PR.

## Files Modified
- `plugin/encypher-provenance/includes/class-encypher-provenance-frontend.php`
