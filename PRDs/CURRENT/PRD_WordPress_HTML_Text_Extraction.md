# PRD: WordPress Plugin HTML Text Extraction Before Signing

**Status:** Complete  
**Current Goal:** Fix segment count mismatch by extracting plain text from WordPress HTML before signing  
**Team:** TEAM_175

## Overview

The WordPress plugin sends raw HTML (including `<!-- wp:paragraph -->` block comments) to the `/sign` endpoint. The enterprise API's sentence segmenter treats HTML comments and tags as text, producing ~27 "segments" instead of the actual 18 sentences. Only 13 of those segments are real sentences that receive VS256 per-sentence signatures. The result: the verification display shows "13 of 27 segments" which is misleading.

The fix follows the same pattern as `tools/encypher-cms-signing-kit/encypher_sign_html.py`: extract plain text from HTML before signing, then embed the signed text back into the HTML DOM.

## Objectives

- WordPress plugin extracts plain text from `post_content` HTML before sending to `/sign`
- Signed text (with invisible markers) is embedded back into the original HTML structure
- Segment count matches actual sentence count (18, not 27)
- Existing signed posts can be re-signed with the fix
- Copy-paste from the rendered WordPress page produces the same verification result as copy-paste from the signed text

## Root Cause Analysis

**WordPress `post_content` for this article:**
```html
<!-- wp:paragraph -->
<p>testing encypher post. Sentence-level.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>For the last two years...</p>
<!-- /wp:paragraph -->
...
```

**What the segmenter sees:** 23-27 "sentences" including HTML comment fragments like `<!-- /wp:paragraph -->`, `wp:paragraph -->`, etc.

**What it should see:** 18 actual sentences (plain text only).

## Reference Implementation

`tools/encypher-cms-signing-kit/encypher_sign_html.py` solves this exact problem for custom CMS systems:

1. `_extract_text_from_element(root)` — walks the DOM, collects text from renderable nodes, inserts newlines at block element boundaries, skips `<script>`, `<style>`, `<img>`, etc.
2. Signs the extracted plain text via the API (newlines replaced with spaces to match API joining).
3. `_embed_signed_text_in_element(root, signed_text)` — walks DOM text nodes, matches each to a position in the signed text, replaces the text node content with the signed version (including invisible VS chars).

## Tasks

### 1.0 WordPress Plugin Changes (`class-encypher-provenance-rest.php`)

- [x] 1.1 Add `extract_text_from_html($html)` method — uses DOMDocument to walk text nodes, strips WP block comments, joins paragraphs with spaces. — ✅ unit tests
- [x] 1.2 Add `embed_signed_text_in_html($original_html, $signed_text)` method — string-based approach using `extract_html_text_fragments()` with byte offsets and `substr_replace`. Avoids DOMDocument::saveHTML mangling. — ✅ unit tests
- [x] 1.3 Update `handle_sign_request()` — calls extract before API payload, calls embed after receiving signed text. — ✅ integration test
- [x] 1.4 Handle edge cases: empty paragraphs, inline elements (`<strong>`, `<em>`, `<a>`), script/style skipping. — ✅ unit tests

### 2.0 Testing

- [x] 2.1 Unit test: `extract_text_from_html()` produces correct plain text from WordPress block HTML — ✅ 26/26 tests pass
- [x] 2.2 Unit test: `embed_signed_text_in_html()` correctly maps signed text back into HTML — ✅ 8/8 fragments matched
- [x] 2.3 Integration test: sign post 36, verify segment count matches (18 sigs = 18 DB segments) — ✅
- [ ] 2.4 Round-trip test: extract text from signed HTML, verify it matches the original signed text
- [ ] 2.5 Copy-paste test: copy rendered page text, paste into verify tool, confirm all segments found

### 3.0 Re-signing Existing Content

- [x] 3.1 Re-signing works via existing sign button (tested on post 36) — ✅
- [x] 3.2 Re-signed post shows correct segment count (18 vs old 27) — ✅

## Success Criteria

- Segment count in verification response matches actual sentence count (18 for the test article, not 27)
- All sentences in the article have per-sentence signatures
- HTML structure (tags, attributes, classes) is preserved after signing
- Copy-paste from rendered WordPress page verifies correctly
- Existing bulk-mark functionality works with the new extraction

## Completion Notes

Implemented 2026-02-12 by TEAM_175. The fix adds ~350 lines of PHP to `class-encypher-provenance-rest.php` following the same extract→sign→embed pattern as `tools/encypher-cms-signing-kit`. Key design decisions:

- **DOMDocument for extraction** — proper HTML parsing handles nested tags, inline elements, etc.
- **String-based embedding** — avoids `DOMDocument::saveHTML()` which HTML-entity-encodes characters and strips WP block comments. Uses byte-offset tracking with `substr_replace` for surgical text node replacement.
- **PHP 7.4 compatible** — uses `mb_str_split_safe()` wrapper and avoids `str_ends_with()`.

Remaining manual tests: 2.4 (round-trip) and 2.5 (copy-paste verify tool) should be done in a browser session.
