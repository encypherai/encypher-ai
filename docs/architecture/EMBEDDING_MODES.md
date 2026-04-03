# Embedding Modes Reference

**Version 2.0 | March 2026**
**Status:** Current -- reflects production implementation

> **Terminology:** See `TERMINOLOGY.md` for canonical names. Customer/marketing term:
> **provenance markers** (consistent with "Content Provenance" positioning). Technical terms:
> **VS markers** (`legacy_safe=false`, recommended default, C2PA-aligned) and **ZWC markers**
> (`legacy_safe=true`, legacy-compatible, Microsoft Word-safe).

---

## Overview

Encypher supports two `manifest_mode` values for signing text content: `full` and `micro`.
Both modes embed cryptographically signed provenance data using invisible Unicode markers.

All modes share the same core architecture:
- **Sentence-level Merkle tree** authentication (patent-pending ENC0100)
- **HMAC-SHA256** cryptographic proof per segment
- **Database-backed** — embedded marker references full metadata, C2PA manifest, license info
- **Public verification** — anyone can verify signed content via API or verification page

---

## manifest_mode: full

C2PA 2.3 manifest embedded into the text using Variation Selector characters.

- Single C2PA wrapper per document
- Standard provenance chain support (`c2pa.created`, `c2pa.edited`)
- Not compatible with Microsoft Word (Variation Selectors render as box glyphs in Word)

**API:**
```json
{ "options": { "manifest_mode": "full" } }
```

---

## manifest_mode: micro

Ultra-compact per-segment HMAC markers plus an optional C2PA document wrapper.
Three boolean flags control the exact sub-mode:

| Flag | Default | Effect |
|------|---------|--------|
| `ecc` | `true` | Enable Reed-Solomon error correction |
| `legacy_safe` | `false` | Use Word-safe base-6 encoding instead of VS256 |
| `embed_c2pa` | `true` | Embed C2PA manifest into the document content |

### Sub-modes

| Sub-mode | `legacy_safe` | `ecc` | Chars/segment | Alphabet | Word-safe |
|----------|--------------|-------|--------------|----------|-----------|
| VS256 | false | false | 36 | 256 Variation Selectors | No |
| VS256-RS | false | true | 44 | 256 Variation Selectors + RS(40,32) | No |
| legacy_safe | true | false | 100 | 6 base-6 ZW chars (ZWNJ/ZWJ/CGJ/MVS/LRM/RLM) | Yes |
| legacy_safe_rs | true | true | 112 | 6 base-6 ZW chars + RS(36,32) | Yes |

### VS256 / VS256-RS

Uses all 256 Unicode Variation Selectors as a base-256 alphabet.

- VS1-VS16 (BMP): U+FE00 - U+FE0F
- VS17-VS256 (Supplementary): U+E0100 - U+E01EF

**VS256 layout (36 chars):**
- Log ID: 16 chars (16 bytes, database reference)
- HMAC-SHA256/128: 16 chars (128-bit truncated)
- Magic prefix: 4 chars (VS240-VS243, format marker)

**VS256-RS layout (44 chars):**
- Log ID: 16 chars
- HMAC-SHA256/64: 8 chars (64-bit truncated)
- RS parity: 8 chars (RS GF(256), 8 parity symbols)
- Magic prefix: 4 chars

RS(40,32): corrects up to 4 unknown errors or 8 known erasures. Poppler drops ~2-3 VS chars on average from a contiguous block -- within the 8-erasure capacity.

**Platform compatibility:**
| Platform | VS256 / VS256-RS |
|----------|-----------------|
| Google Docs | Renders invisibly |
| Web browsers | Renders invisibly |
| PDF (TrueType/OpenType) | Survives signing + extraction |
| PDF (Type3 fonts) | Verification works; copy-paste limited in Chrome |
| Microsoft Word | Shows box glyphs -- use legacy_safe instead |

### legacy_safe / legacy_safe_rs

Uses 6 confirmed Word-safe and terminal-safe invisible characters as a base-6 alphabet:

| Char | Codepoint | Digit |
|------|-----------|-------|
| ZWNJ | U+200C | 0 |
| ZWJ | U+200D | 1 |
| CGJ | U+034F | 2 |
| MVS | U+180E | 3 |
| LRM | U+200E | 4 |
| RLM | U+200F | 5 |

Big-number base-6 encoding: the full 32-byte (or 36-byte RS) payload is treated as one
large integer and encoded in base-6, achieving ~99.5% Shannon efficiency.

**Characters NOT used:** ZWSP (U+200B) -- stripped by Word during copy-paste.

**legacy_safe layout (100 chars):**
- Log ID: 16 bytes
- HMAC-SHA256/128: 16 bytes
- Total: 32 bytes -> 100 base-6 chars (ceil(256 * log2 / log6) = 100)

**legacy_safe_rs layout (112 chars):**
- Log ID: 16 bytes
- HMAC-SHA256/128: 16 bytes
- RS(36,32) parity: 4 bytes
- Total: 36 bytes -> 112 base-6 chars (ceil(288 * log2 / log6) = 112)

RS(36,32): corrects up to 2 unknown errors or 4 known erasures.

**Detection:** A 100-char (or 112-char) run from the 6-char set that contains at least
one LRM or RLM is treated as a legacy_safe (or legacy_safe_rs) marker. LRM/RLM are absent
from the old base-4 alphabet, making them unambiguous discriminators.

**Platform compatibility:**
| Platform | legacy_safe / legacy_safe_rs |
|----------|------------------------------|
| Microsoft Word | Survives copy-paste |
| Google Docs | Renders invisibly |
| PDF (all font types) | Survives signing + extraction |
| Web browsers | Renders invisibly |
| Standard terminals | No visual artifact |

---

## embed_c2pa flag

For `micro` mode, `embed_c2pa` controls whether the C2PA document manifest is also
embedded into the signed content:

- `embed_c2pa=true` (default): per-segment markers + C2PA manifest wrapper embedded
- `embed_c2pa=false`: per-segment markers only; C2PA manifest is still generated and
  stored in the database for API-based verification

A C2PA manifest is always generated and always stored in the DB (controlled separately
by `store_c2pa_manifest`). `embed_c2pa` only controls whether it appears inside the
returned `signed_text`.

---

## Quick Selection Guide

- **Need Microsoft Word compatibility?** -> Use `legacy_safe=true` (micro mode)
- **Need maximum density?** -> Use VS256-RS (micro mode, ecc=true, legacy_safe=false), 44 chars/segment
- **Need error correction for lossy pipelines?** -> Enable `ecc=true`
- **Need full C2PA manifest embedded in content?** -> Use `full` mode or `micro` with `embed_c2pa=true`
- **Signing PDFs?** -> VS256-RS recommended (ecc=true, legacy_safe=false)

---

## API Usage

### Signing (Enterprise API)

```bash
# Full mode (default, C2PA manifest in content)
curl -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Article text...",
    "options": { "manifest_mode": "full" }
  }'

# Micro mode: VS256-RS (max density, ECC, not Word-safe)
curl -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Article text...",
    "options": {
      "manifest_mode": "micro",
      "ecc": true,
      "legacy_safe": false
    }
  }'

# Micro mode: legacy_safe-RS (Word-safe, ECC)
curl -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Article text...",
    "options": {
      "manifest_mode": "micro",
      "ecc": true,
      "legacy_safe": true
    }
  }'
```

---

## PDF-Specific Behavior

When signing an existing PDF, Encypher uses a **font-switching injection** approach:

1. The original PDF content streams and fonts are left completely untouched
2. A custom CID font (`EncSgn`) containing only invisible glyphs is embedded in the PDF
3. Invisible characters are injected inline via font-switch sequences
4. The signed text is also stored in an `EncypherSignedText` metadata stream for reliable extraction

This approach preserves visual rendering for all font types, including Type3 and custom-encoded fonts.

### PDF Font Compatibility

| Font Type | Visual Rendering | Copy-Paste (pdftotext) | Verification |
|-----------|-----------------|----------------------|-------------|
| TrueType / OpenType | Perfect | VS/ZW chars preserved | Always works |
| Type1 (base-14) | Perfect | VS/ZW chars preserved | Always works |
| CID-keyed | Perfect | VS/ZW chars preserved | Always works |
| Type3 (custom encoding) | Perfect | VS/ZW chars preserved | Always works |

Verification always works because it uses the `EncypherSignedText` metadata stream, not copy-paste.

---

## Size Impact

For a 1,000-word article (~50 sentences):

| Sub-mode | Chars added | Overhead |
|----------|------------|---------|
| VS256 (ecc=false, legacy_safe=false) | 1,800 | ~0.5% |
| VS256-RS (ecc=true, legacy_safe=false) | 2,200 | ~0.6% |
| legacy_safe (ecc=false, legacy_safe=true) | 5,000 | ~1.5% |
| legacy_safe_rs (ecc=true, legacy_safe=true) | 5,600 | ~1.7% |
| full (C2PA manifest) | ~25,000 | ~7-10% |

---

## Verification

All modes are verified through the same endpoint. The verification service auto-detects
the embedding format in priority order:

1. **legacy_safe_rs** (112-char base-6, LRM/RLM, RS decode) -- tried first
2. **legacy_safe** (100-char base-6, LRM/RLM) -- tried if RS decode fails
3. **VS256-RS** (magic prefix + RS decode) -- tried next
4. **VS256** (magic prefix, no RS) -- tried if RS decode fails
5. **C2PA manifest** -- tried for full mode

```bash
curl -X POST https://api.encypher.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "Text with invisible embeddings..."}'
```

---

## Email Survivability

No single invisible encoding is universally robust through every email pipeline:

| Transform | VS256 / VS256-RS | legacy_safe / legacy_safe_rs |
|-----------|-----------------|------------------------------|
| Unicode NFC normalization | Survives | Survives |
| Strip supplementary VS (VS17-VS256) | Breaks | Survives |
| Strip all variation selectors | Breaks | Survives |
| Strip format-control zero-widths | Survives | Breaks |

**Recommended strategy:** Use `legacy_safe=true` for email workflows; use VS256-RS for
web/PDF workflows.

---

## Security Summary

| Sub-mode | Log ID bits | HMAC bits | Error correction |
|----------|------------|-----------|-----------------|
| VS256 | 128 | 128 | None |
| VS256-RS | 128 | 64 | RS(40,32): 4 errors / 8 erasures |
| legacy_safe | 128 | 128 | None |
| legacy_safe_rs | 128 | 128 | RS(36,32): 2 errors / 4 erasures |
| full (C2PA) | 128 | 256 (Ed25519) | None |

VS256-RS uses 64-bit HMAC because primary verification is database lookup (log ID -> org),
not HMAC-alone brute force. legacy_safe_rs retains full 128-bit HMAC because the base-6
encoding has headroom for 4 RS parity bytes at no HMAC cost.

---

*Last updated: March 2026 -- TEAM_248*
