# Embedding Modes Reference

**Version 2.1 | April 2026**
**Status:** Current -- reflects production implementation

> **Terminology:** See `TERMINOLOGY.md` for canonical names. Customer/marketing term:
> **provenance markers** (consistent with "Content Provenance" positioning). Technical terms:
> **VS markers** (`legacy_safe=false`, recommended default, C2PA-aligned), **ZWC markers**
> (`legacy_safe=true`, legacy-compatible, Microsoft Word-safe), and **print-space markers**
> (`enable_print_micro_ecc=true`, Enterprise, survives print/scan).

---

## Overview

Encypher supports two `manifest_mode` values for signing text content: `full` and `micro`.
Both modes embed cryptographically signed provenance data using invisible Unicode markers.

A third channel, **Print-Survivable Micro ECC**, operates alongside the primary signing mode
as a parallel embedding layer. It encodes the same `log_id` + HMAC payload in inter-word
spacing width variations, enabling provenance verification from printed and scanned copies.

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

## Print-Survivable Micro ECC (Enterprise)

A parallel embedding channel that encodes provenance data in inter-word spacing width
variations. Unlike VS and ZWC markers (which use invisible Unicode characters), print-space
markers use physically distinguishable Unicode space variants whose width differences survive
the rasterize-print-scan-OCR pipeline at institutional quality levels (300-600 DPI).

Activated via `enable_print_micro_ecc=true` in SignOptions. Enterprise tier only. Mutually
exclusive with `enable_print_fingerprint` (the legacy 128-bit lookup-key-only variant).

### Alphabet (4 symbols, ordered by ascending physical width)

| Symbol | Codepoint | Name | Width |
|--------|-----------|------|-------|
| 0 | U+200A | HAIR SPACE | ~0.1 em |
| 1 | U+2006 | SIX-PER-EM SPACE | ~0.167 em |
| 2 | U+2009 | THIN SPACE | ~0.2 em |
| 3 | U+0020 | REGULAR SPACE | ~0.25 em |

### Layout (48 bytes -> 192 inter-word positions)

```
[log_id: 16 bytes] [HMAC-SHA256/128: 16 bytes] [RS parity: 16 bytes]
 = 48 bytes = 384 bits = 192 base-4 symbols (2 bits per position)
```

RS(48,32) over GF(256): 16 parity symbols, corrects up to 8 unknown byte errors or 16
known-position erasures. Doubled parity vs the digital VS256-RS channel provides margin
for the tighter decision boundaries in the physical print/scan channel.

### Interleaving

Encoded positions are spread evenly across the full document (not front-loaded). For N
required positions out of M available inter-word spaces: `idx[i] = floor(i * M / N)`.
This distributes RS-correctable errors across the full document, so a localized OCR
failure (burst error) affects non-adjacent RS symbols.

### Minimum document size

192 inter-word positions = 193 words minimum. Documents shorter than this are returned
unmodified (graceful no-op with a warning).

### Platform compatibility

| Transform | Print Micro ECC |
|-----------|----------------|
| PDF copy-paste | Survives (space codepoints preserved) |
| High-quality print/scan (300-600 DPI) | Survives (space-width classification + RS recovery) |
| ZWC/VS stripping | Survives (orthogonal channel, uses only space chars) |
| Aggressive whitespace normalization | Lost (all spaces collapsed to U+0020) |
| Low-quality OCR (< 150 DPI) | May be lost (insufficient pixel resolution) |
| Plain-text email (MUA normalization) | Lost (spaces normalized) |

### Print vs. legacy print fingerprint

| | Print Micro ECC | Print Fingerprint (legacy) |
|---|---|---|
| Payload | log_id (16 B) + HMAC (16 B) | HMAC only (16 B) |
| Error correction | RS(48,32): 8 errors / 16 erasures | None |
| Positions needed | 192 (~193 words) | 128 (~129 words) |
| Alphabet | 4 symbols (base-4) | 2 symbols (binary) |
| Self-contained verification | Yes (log_id -> transparency log) | No (needs publisher key + DB match) |
| API flag | `enable_print_micro_ecc` | `enable_print_fingerprint` |

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
- **Need provenance to survive printing and scanning?** -> Use `enable_print_micro_ecc=true` (Enterprise, requires >= 193 words)

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

# Print-survivable Micro ECC (Enterprise, parallel channel)
# Adds print-space markers alongside the primary signing mode.
# Requires >= 193 words. Mutually exclusive with enable_print_fingerprint.
curl -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Government document text (>= 193 words)...",
    "options": {
      "manifest_mode": "micro",
      "ecc": true,
      "enable_print_micro_ecc": true
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
| Print Micro ECC (parallel channel) | 0 new chars | ~0% (replaces 192 existing spaces with width variants) |

---

## Verification

All modes are verified through the same endpoint. The verification service auto-detects
the embedding format in priority order:

1. **legacy_safe_rs** (112-char base-6, LRM/RLM, RS decode) -- tried first
2. **legacy_safe** (100-char base-6, LRM/RLM) -- tried if RS decode fails
3. **VS256-RS** (magic prefix + RS decode) -- tried next
4. **VS256** (magic prefix, no RS) -- tried if RS decode fails
5. **C2PA manifest** -- tried for full mode
6. **Print Micro ECC** (space-width classification, RS decode) -- detected in parallel via `detect_print_micro_ecc` (default: true). Returns `log_id_hex` and `hmac_hex` in `details.print_micro_ecc`
7. **Print fingerprint** (thin-space binary) -- detected in parallel via `detect_print_fingerprint` (default: true). Returns `payload_hex` in `details.print_fingerprint`

```bash
curl -X POST https://api.encypher.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "Text with invisible embeddings..."}'
```

---

## Email Survivability

No single invisible encoding is universally robust through every email pipeline:

| Transform | VS256 / VS256-RS | legacy_safe / legacy_safe_rs | Print Micro ECC |
|-----------|-----------------|------------------------------|----------------|
| Unicode NFC normalization | Survives | Survives | Survives |
| Strip supplementary VS (VS17-VS256) | Breaks | Survives | Survives (orthogonal) |
| Strip all variation selectors | Breaks | Survives | Survives (orthogonal) |
| Strip format-control zero-widths | Survives | Breaks | Survives (orthogonal) |
| Whitespace normalization | Survives | Survives | Breaks |
| Print -> scan -> OCR | Breaks | Breaks | Survives |

**Recommended strategy:** Use `legacy_safe=true` for email workflows; use VS256-RS for
web/PDF workflows. Add `enable_print_micro_ecc=true` for documents that will be printed.

---

## Security Summary

| Sub-mode | Log ID bits | HMAC bits | Error correction |
|----------|------------|-----------|-----------------|
| VS256 | 128 | 128 | None |
| VS256-RS | 128 | 64 | RS(40,32): 4 errors / 8 erasures |
| legacy_safe | 128 | 128 | None |
| legacy_safe_rs | 128 | 128 | RS(36,32): 2 errors / 4 erasures |
| full (C2PA) | 128 | 256 (Ed25519) | None |
| Print Micro ECC | 128 | 128 | RS(48,32): 8 errors / 16 erasures |

VS256-RS uses 64-bit HMAC because primary verification is database lookup (log ID -> org),
not HMAC-alone brute force. legacy_safe_rs retains full 128-bit HMAC because the base-6
encoding has headroom for 4 RS parity bytes at no HMAC cost. Print Micro ECC uses doubled
RS parity (16 symbols vs 8) because the physical print/scan channel has tighter decision
boundaries between space-width symbols (minimum gap: 0.033 em).

---

*Last updated: April 2026 -- TEAM_297 (Print Micro ECC), TEAM_248 (prior)*
