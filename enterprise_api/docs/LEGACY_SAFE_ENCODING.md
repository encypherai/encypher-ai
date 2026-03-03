# Base-6 Legacy-Safe Zero-Width Encoding

## Overview

`legacy_safe` is the second generation of Encypher's Word-safe invisible embedding format.
It supersedes the base-4 format for new content, reducing the per-sentence marker from
128 characters to 100 characters -- a 22% reduction -- while maintaining 128-bit HMAC
security and identical platform compatibility.

The gains come from a single key improvement:

1. **Alphabet expansion** -- empirical testing of 27 Unicode candidate characters
   confirmed two additional Word-safe invisible chars (LRM and RLM), expanding the
   encoding base from 4 to 6 symbols.

The payload size is identical to base-4 at 32 bytes (16-byte log_id + 16-byte HMAC),
designed to be safe at hyperscale deployment across the global AI ecosystem.

---

## Background: Why a New Format Was Needed

The base-4 format uses exactly four Unicode characters that were empirically confirmed
to survive Microsoft Word copy/paste:

| Char | U+ | Category |
|------|----|----------|
| ZWNJ | 200C | Cf |
| ZWJ  | 200D | Cf |
| CGJ  | 034F | Mn |
| MVS  | 180E | Cf |

With only four symbols, log2(4) = 2 bits per character is the Shannon limit -- no
encoding trick can beat it. The 128-character marker for 32 bytes of payload is the
theoretical minimum for this alphabet.

The only path to compression was:
- Expand the alphabet (more symbols = more bits per character)

---

## Research: Alphabet Expansion

### Methodology

A test tool was built to systematically evaluate Unicode candidates. Each candidate
was embedded as 10 contiguous copies between visible `>>` / `<<` markers in a test
sentence. Testers copy the full output into Microsoft Word, then copy back out and
paste into the tool's `--verify` mode, which counts surviving characters per codepoint.

27 candidates were evaluated across six Unicode categories:

- Directional format chars: LRM (U+200E), RLM (U+200F)
- Invisible math operators: FUNC (U+2061), ITIMES (U+2062), ISEP (U+2063), IPLUS (U+2064)
- Deprecated format chars: ISS (U+206A) through NODS (U+206F)
- Unicode Plane 14 tag chars: U+E0020 through U+E007F (sample)
- Other: ZWSP (U+200B), WJ (U+2060), ZWNBSP (U+FEFF), SHY (U+00AD), U+2028

### Results (desktop Microsoft Word, March 2026)

| Candidate | Result | Notes |
|-----------|--------|-------|
| LRM U+200E | **PASS - no visual artifact** | Confirmed safe |
| RLM U+200F | **PASS - no visual artifact** | Confirmed safe |
| WJ U+2060 | Survives but visible | Renders as space character |
| FUNC U+2061 | Survives but visual artifact | Not suitable |
| ITIMES U+2062 | Survives but visual artifact | Not suitable |
| ISEP U+2063 | Survives but visual artifact | Not suitable |
| IPLUS U+2064 | Survives but visual artifact | Not suitable |
| ISS-NODS U+206A-206F | Survives but visual artifact | Also deprecated (risky) |
| TAG chars U+E0020+ | Partial survival, corruption | Surrogate pair issues |
| ZWSP U+200B | Stripped | Known, documented |
| ZWNBSP U+FEFF | Stripped | Stripped |
| U+2028 | Causes line break | Wrong character class |
| SHY U+00AD | Survives but visible at line breaks | Not suitable |

**Outcome:** Only LRM and RLM pass without any visual artifact. All other candidates
either introduce visible rendering changes in Word or have unreliable survival.

### Confirmed Word-Safe and Terminal-Safe Alphabet (6 symbols)

| Symbol | Codepoint | Name | Status |
|--------|-----------|------|--------|
| 0 | U+200C | Zero-Width Non-Joiner (ZWNJ) | original |
| 1 | U+200D | Zero-Width Joiner (ZWJ) | original |
| 2 | U+034F | Combining Grapheme Joiner (CGJ) | original |
| 3 | U+180E | Mongolian Vowel Separator (MVS) | original |
| 4 | U+200E | Left-to-Right Mark (LRM) | **new** |
| 5 | U+200F | Right-to-Left Mark (RLM) | **new** |

LRM and RLM are Unicode category Cf (Format), like ZWNJ and ZWJ. They have no
visual rendering in LTR text and no effect on text layout when embedded between
characters within a run of the same directionality (i.e., in normal English text).

---

## Encoding: Big-Number Base-6

### Why Not Byte-by-Byte?

Base-6 byte-by-byte encoding does not work at 4 chars/byte because 6^3 = 216 < 256
(three base-6 digits cannot represent all 256 byte values). Stepping up to 4 chars/byte
gives 6^4 = 1296, which wastes 80% of the available encoding space -- no better in
practice than base-4.

The solution is **big-number encoding**: treat the entire payload as one large integer
and convert it to base-6, rather than encoding each byte independently.

### Big-Number Encoding

```
payload_integer = int.from_bytes(payload_bytes, "big")
digits = []
while payload_integer > 0:
    digits.append(CHARS_BASE6[payload_integer % 6])
    payload_integer //= 6
# left-pad with ZWNJ (digit 0) to fixed length
```

For a 32-byte (256-bit) payload, the required length is:

```
ceil(256 * log(2) / log(6)) = ceil(99.03) = 100 digits
```

Verified: 6^100 ~ 6.5 * 10^77 > 2^256 ~ 1.16 * 10^77. Exactly 100 characters
always suffice to represent any 32-byte value.

Shannon efficiency: log2(6^100) / 256 = 258.5 / 256 = 99.9% -- essentially lossless.

**Tradeoff:** The entire payload must be decoded as a unit. Individual bytes cannot be
extracted from a partial marker. In practice this is not a constraint -- verification
always processes the full 100-character marker.

---

## Payload: Log ID Design

### Payload Format (32 bytes)

```
[log_id: 16 bytes] [HMAC-SHA256/128: 16 bytes]
```

The `log_id` is a 16-byte random identifier that references an entry in the
attestation transparency log.

### Why 16 Bytes: Hyperscale Collision Analysis

Encypher's technology is designed to be licensed to global AI platforms -- OpenAI,
Anthropic, Google, Meta, and others. At those deployment scales:

- ChatGPT alone processes ~2.5 billion messages/day (March 2026)
- The global AI ecosystem exceeds ~20 billion messages/day when all major providers
  are considered

For a 128-bit (16-byte) log_id at 20B messages/day:
- Birthday collision threshold (50%): N ~ sqrt(2^128) ~ 1.8 * 10^19 entries
- Time to threshold at 20B/day: ~2.5 * 10^9 years
- P(any collision) over 10 years: ~2e-12 (negligible)
- **Conclusion: 16-byte IDs are safe at any realistic AI deployment scale indefinitely.**

### Random vs Sequential ID

**Sequential IDs (auto-increment integers) were considered and rejected.**

A sequential log ID would disclose signing volume: any party receiving a signed
document can read the embedded ID and infer how many documents the organization
has signed up to that point. This is a business intelligence leak.

**The chosen approach: random 16-byte IDs (os.urandom(16)).**

Random IDs provide the same collision safety with no volume disclosure. The only
property lost is ordering: transparency log consistency proofs use the log's internal
append sequence, not the embedded ID.

---

## Detection

Legacy-safe markers are detected by scanning for contiguous runs of characters from
the 6-symbol set, then filtering to runs of exactly 100 characters that contain at
least one LRM (U+200E) or RLM (U+200F).

The LRM/RLM requirement is the key discriminator:
- Base-4 markers (128 chars) never contain LRM or RLM -- they use only ZWNJ/ZWJ/CGJ/MVS
- legacy_safe markers (100 chars) almost always contain LRM or RLM: probability of a
  random 256-bit payload having no base-6 digits 4 or 5 is (4/6)^100 ~ 2 * 10^-18

This means a 100-char run of base-4 characters will not be misidentified as a
legacy_safe marker, even though the alphabets overlap.

Length and symbol presence together are unambiguous in all realistic cases.

---

## Security Properties

| Property | legacy_safe |
|----------|-------------|
| HMAC security | 128-bit (16 bytes) |
| ID uniqueness | 128-bit random log_id |
| Content binding | SHA256(NFC(text))[:8] in HMAC |
| Signing key | Org Ed25519 private key derivation |
| Tamper detection | HMAC fails on any modification |
| Forgery resistance | 2^128 HMAC brute force |
| Collision safety | P~2e-12 / 10yr at 20B/day |

The HMAC over `log_id || SHA256(sentence)[:8]` binds the marker to both the specific
log entry and the exact sentence content. A forged marker requires either:
- Finding a log_id that produces the correct HMAC (2^128 operations), or
- Obtaining the org's signing key

Neither is feasible.

---

## Size Comparison

| Format | Module | Payload | Chars | vs base-4 |
|--------|--------|---------|-------|-----------|
| base-4 (legacy) | (deleted) | 32 bytes (UUID + HMAC) | **128** | baseline |
| legacy_safe | legacy_safe_crypto.py | 32 bytes (log_id + HMAC) | **100** | **-22%** |
| legacy_safe_rs | legacy_safe_rs_crypto.py | 32 bytes + 4 RS parity | **112** | -12% (with ECC) |
| VS256 (micro) | vs256_crypto.py | 32 bytes | 36 | -72% (not Word-safe) |
| VS256-RS (micro + ecc) | vs256_rs_crypto.py | 32 bytes + 8 RS parity | 44 | -66% (not Word-safe) |

For a document with 20 sentences:
- base-4: 20 x 128 = 2,560 invisible characters
- legacy_safe: 20 x 100 = 2,000 invisible characters

The 22% reduction is achieved entirely from alphabet expansion (4 -> 6 symbols).

---

## API

### Creating a Marker

```python
from app.utils.legacy_safe_crypto import (
    generate_log_id,
    create_marker,
    create_embedded_sentence,
    derive_signing_key_from_private_key,
)

signing_key = derive_signing_key_from_private_key(org_private_key)

# Per-sentence signing
for sentence in sentences:
    log_id = generate_log_id()  # 16 random bytes (128-bit, hyperscale-safe)

    # Option A: marker only
    marker = create_marker(log_id, signing_key, sentence_text=sentence)

    # Option B: embed directly (positions before terminal punctuation)
    signed_sentence = create_embedded_sentence(sentence, log_id, signing_key)

    # Store log_id -> {org, document, sentence, merkle_proof, ...} in transparency log
    log.register(log_id, metadata={...})
```

### Verifying a Marker

```python
from app.utils.legacy_safe_crypto import find_all_markers, verify_marker

markers = find_all_markers(text)           # [(start, end, marker_str), ...]

for start, end, marker_str in markers:
    ok, log_id = verify_marker(marker_str, signing_key, sentence_text=sentence)
    if ok:
        record = log.get(log_id)           # retrieve full metadata from log
```

### Detection Only (no key required)

```python
from app.utils.legacy_safe_crypto import find_all_markers, extract_marker, remove_markers

markers = find_all_markers(text)           # list all
marker  = extract_marker(text)             # first only, or None
clean   = remove_markers(text)             # strip all markers
```

---

## Testing

### Automated tests

```bash
cd enterprise_api
uv run pytest tests/test_legacy_safe_crypto.py -v
```

Coverage includes:
- Encode/decode roundtrip for all 256 byte values
- Marker creation and HMAC verification (correct key)
- HMAC rejection (wrong key, tampered content)
- Content binding (sentence_text changes fail HMAC)
- Detection in clean text and mixed-format text
- No false positives from base-4 markers
- Safe embedding before terminal punctuation

---

## Files

| Path | Purpose |
|------|---------|
| `app/utils/legacy_safe_crypto.py` | Encoder, decoder, detection, embedding |
| `app/utils/legacy_safe_rs_crypto.py` | RS(36,32) ECC variant (112 chars) |
| `docs/LEGACY_SAFE_ENCODING.md` | This document |
