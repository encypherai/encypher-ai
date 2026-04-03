# PRD: WordPress Plugin Public Release

## Status: COMPLETED

## Current Goal
Make WordPress plugin 100% bulletproof, aligned UX/UI, and ready for public release with fully compliant C2PA embeddings.

## Overview
Prepare the Encypher Provenance WordPress plugin for public release on WordPress.org. This includes fixing deprecated API endpoint usage, ensuring C2PA compliance, aligning branding, and creating WordPress.org-compliant readme.txt.

## Objectives
- Fix deprecated endpoint references
- Ensure C2PA embedding compliance
- Align UX/UI with Encypher branding
- Create WordPress.org-compliant readme.txt
- Bump version for release

## Tasks

### 1.0 Plugin Audit
- [x] 1.1 Review plugin structure and files ✅
- [x] 1.2 Identify deprecated endpoint usage ✅

### 2.0 Fix Deprecated Endpoints
- [x] 2.1 Update `/public/extract-and-verify` to `/verify` in REST class ✅
- [x] 2.2 Update documentation references ✅

### 3.0 UX/UI Alignment
- [x] 3.1 Verify Encypher brand colors in CSS ✅ (Deep Navy #1B2F50, Azure Blue #2A87C4)
- [x] 3.2 Verify Roboto font usage ✅
- [x] 3.3 Check icon and logo assets ✅

### 4.0 WordPress.org Compliance
- [x] 4.1 Create readme.txt with proper format ✅
- [x] 4.2 Bump version to 1.1.0 ✅
- [x] 4.3 Verify GPL-2.0-or-later license ✅
- [x] 4.4 Verify text domain and i18n setup ✅

### 5.0 C2PA Compliance Verification
- [x] 5.1 Single wrapper per document ✅ (verified in detect_c2pa_embeddings)
- [x] 5.2 Proper action types (c2pa.created, c2pa.edited) ✅
- [x] 5.3 Provenance chain support ✅
- [x] 5.4 Unicode variation selector embedding ✅

## Success Criteria
- All deprecated endpoint references removed
- WordPress.org readme.txt created
- Version bumped to 1.1.0
- C2PA compliance validated
- Branding consistent with Encypher standards

## Completion Notes
Completed on Feb 5, 2026.

**Changes Made:**
1. **REST Endpoint Fix**: Updated `handle_public_extract_request()` to use `/verify` instead of deprecated `/public/extract-and-verify`
2. **Documentation Updates**: Updated README.md files to reflect unified `/sign` endpoint
3. **Version Bump**: 1.0.1 → 1.1.0
4. **WordPress.org readme.txt**: Created full readme.txt with proper format for plugin submission

**Plugin Status:**
- ✅ C2PA compliant (single wrapper per document)
- ✅ Auto-sign on publish/update
- ✅ Provenance chain for edits
- ✅ Tier-based feature gating
- ✅ Gutenberg sidebar integration
- ✅ Public verification badge
- ✅ Bulk signing tool
- ✅ Analytics dashboard
- ✅ Coalition membership support

**Files Modified:**
- `plugin/encypher-provenance/encypher-provenance.php` - Version bump
- `plugin/encypher-provenance/includes/class-encypher-provenance-rest.php` - Endpoint fix
- `plugin/encypher-provenance/README.md` - Documentation update
- `README.md` - API endpoint documentation update

**Files Created:**
- `plugin/encypher-provenance/readme.txt` - WordPress.org submission file

**Next Steps for Distribution:**
1. Submit to WordPress.org plugin directory
2. Contact WordPress VIP for enterprise partnership
3. Create marketing landing page at encypher.com/wordpress
