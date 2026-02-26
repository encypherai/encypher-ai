# Zero-Width Embedding Mode (zw_embedding)

## Overview

The `zw_embedding` mode provides **cryptographically signed invisible embeddings** using **base-4 encoding with Word-safe Unicode characters**, making it compatible with **Microsoft Word, Google Docs, PDF, and all major document platforms**.

Unlike the default variation selector approach, `zw_embedding` uses a carefully selected set of invisible characters that survive Microsoft Word's copy/paste operations.

## Key Features

✅ **Word-Compatible** - Uses only characters Word preserves (no ZWSP!)  
✅ **Cryptographically Signed** - Full Ed25519 signatures or HMAC-SHA256  
✅ **Tamper Detection** - Content hash verification detects modifications  
✅ **Cross-Platform** - Works in Word, Google Docs, PDF, browsers, mobile  
✅ **Compact** - Base-4 encoding: 132 chars per sentence signature  
✅ **No Font Dependencies** - Invisible characters guaranteed by Unicode spec

## Word Compatibility Discovery

**Critical finding:** Microsoft Word strips ZWSP (U+200B) during copy/paste operations!

After extensive testing, we identified **4 invisible characters that Word preserves**:

| Character | Code Point | Name | Word Status |
|-----------|------------|------|-------------|
| **ZWNJ** | U+200C | Zero-Width Non-Joiner | ✅ Preserved |
| **ZWJ** | U+200D | Zero-Width Joiner | ✅ Preserved |
| **CGJ** | U+034F | Combining Grapheme Joiner | ✅ Preserved |
| **MVS** | U+180E | Mongolian Vowel Separator | ✅ Preserved |
| ~~ZWSP~~ | ~~U+200B~~ | ~~Zero-Width Space~~ | ❌ **STRIPPED** |  

## How It Works

### Encoding Scheme

**Base-4 Encoding** using four Word-safe invisible characters:
- `ZWNJ` (U+200C) = 0 - Zero-Width Non-Joiner
- `ZWJ` (U+200D) = 1 - Zero-Width Joiner
- `CGJ` (U+034F) = 2 - Combining Grapheme Joiner
- `MVS` (U+180E) = 3 - Mongolian Vowel Separator

Each byte (0-255) is encoded as **4 characters**:
```
4^4 = 256 (exactly enough for all byte values)
```

**This is 33% more compact than base-3 encoding** while being fully Word-compatible!

---

## Minimal Signed UUID (Sentence-Level Embeddings)

**The most compact cryptographically secure per-sentence signature:**

### Format: 132 Characters Total (Base-4)

```
[Magic] [UUID] [HMAC]
4 chars  64 chars  64 chars = 132 chars
```

| Component | Bytes | Chars | Purpose |
|-----------|-------|-------|---------|
| Magic | - | 4 | Format detection (`ZWJ+ZWNJ+CGJ+MVS`) |
| UUID | 16 | 64 | Database reference |
| HMAC-SHA256 | 16 | 64 | Cryptographic proof (128-bit security) |
| **Total** | **32** | **132** | **Per-sentence overhead** |

**33% smaller than base-3 encoding** while being fully Word-compatible!

### Security Properties

- ✅ **128-bit UUID uniqueness** - Collision-resistant identifier
- ✅ **128-bit HMAC security** - Truncated HMAC-SHA256
- ✅ **Org-specific signing key** - Derived from Ed25519 private key
- ✅ **Tamper detection** - Any modification invalidates HMAC
- ✅ **Word-compatible** - Uses ZWNJ, ZWJ, CGJ, MVS (no ZWSP!)

### Usage Example

```python
from app.utils.zw_crypto import (
    create_minimal_signed_uuid,
    verify_minimal_signed_uuid,
    derive_signing_key_from_private_key,
    find_all_minimal_signed_uuids,
    create_safely_embedded_sentence,  # Safe positioning
)

# Derive signing key from org's private key
signing_key = derive_signing_key_from_private_key(org_private_key)

# Sign each sentence (with safe positioning)
for sentence in sentences:
    sentence_uuid = uuid.uuid4()
    
    # Embeds BEFORE terminal punctuation to reduce accidental deletion
    signed_sentence = create_safely_embedded_sentence(
        sentence, sentence_uuid, signing_key
    )
    # Result: "Hello world[196 ZW]." - signature before period
    
    # Store in database
    db.store({
        "uuid": sentence_uuid,
        "sentence_hash": hash(sentence),
        "document_id": doc_id,
        "leaf_index": idx,
        "merkle_proof": proof,
        "full_manifest": manifest,  # All metadata lives in DB
    })

# Verify later
is_valid, extracted_uuid = verify_minimal_signed_uuid(text, signing_key)
if is_valid:
    record = db.get(extracted_uuid)  # Pull full metadata from DB
```

### Safe Embedding Position

To reduce accidental deletion in Word/editors, signatures are embedded **before terminal punctuation**:

```
"Hello world."     → "Hello world[SIG]."
"What time is it?" → "What time is it[SIG]?"
"Wow!"             → "Wow[SIG]!"
'She said "Hi."'   → 'She said "Hi[SIG]."'
"No punctuation"   → "No punctuation[SIG]"
```

**Why this helps:** Users typically delete from the end of text. By placing the invisible signature before punctuation, the punctuation acts as a "buffer" - users delete the period first, giving them visual feedback before they accidentally delete the signature.

**Supported punctuation:** `. ! ? " ' ) ] } » "`

### Size Comparison

| Format | Per-Sentence | 50 Sentences | Notes |
|--------|--------------|--------------|-------|
| **Minimal Signed UUID (Base-4)** | **132 chars** | **6,600 chars** | ✅ Word-compatible |
| Full ZW Signature (Base-4) | ~900 chars | ~45,000 chars | ✅ Word-compatible |
| Old Base-3 (with ZWSP) | 196 chars | 9,800 chars | ❌ Word strips ZWSP |
| Variation Selectors | ~2,000 chars | 100,000 chars | ❌ Word shows □ boxes |

### Verification Flow

```
1. Extract minimal signed UUID from text (132 chars)
2. Verify HMAC using org's signing key
3. If valid → UUID is authentic
4. Lookup UUID in database → Get full metadata:
   - Signer ID, organization
   - Merkle tree info (root hash, leaf index, proof)
   - Full C2PA manifest
   - Timestamp, expiration
   - License info
```

---

### Full Signature Structure (Document-Level)

```
[Magic Number] [Version] [Payload Length] [Payload] [Signature]
     4 chars    4 chars      8 chars       variable   256 chars
```

**Components (Base-4 encoding):**
1. **Magic Number** (4 chars): `ZWJ+ZWNJ+ZWJ+CGJ` - Format detection
2. **Version** (4 chars): Format version (currently v1)
3. **Payload Length** (8 chars): 2-byte length field
4. **Payload** (variable): JSON metadata (signer_id, timestamp, content_hash, etc.)
5. **Signature** (256 chars): Ed25519 signature (64 bytes × 4 chars/byte)

**Total Size:** ~900 characters for typical payload (33% smaller than base-3)

### Example

```python
from app.utils.zw_crypto import create_zw_signature, verify_zw_signature

# Sign text
text = "This is my article content."
signature = create_zw_signature(
    text=text,
    private_key=org_private_key,
    signer_id="org_technews",
    metadata={"document_id": "article_001"}
)

# Embed signature (invisible)
signed_text = text + signature
# Result: "This is my article content.​‌​‍..." (invisible ZW chars)

# Verify signature
is_valid, payload = verify_zw_signature(signed_text, org_public_key)
# Returns: (True, {"signer_id": "org_technews", "content_hash": "...", ...})
```

## API Usage

### Signing Endpoint

**Request:**
```json
POST /api/v1/sign
{
  "document_id": "article_001",
  "text": "Article content...",
  "options": {
    "manifest_mode": "zw_embedding",
    "segmentation_level": "document"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "document": {
      "document_id": "article_001",
      "signed_text": "Article content...‍‌‍͏...",
      "verification_url": "https://verify.encypherai.com/article_001"
    },
    "metadata": {
      "manifest_mode": "zw_embedding",
      "zw_encoding": "base4_word_safe",
      "signature_chars_per_segment": 132
    }
  }
}
```

### Verification Endpoint

**Request:**
```json
POST /api/v1/verify
{
  "text": "Article content...​‌​‍..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "tampered": false,
    "reason_code": "OK",
    "signer_id": "org_technews",
    "signer_name": "TechNews Corp"
  },
  "correlation_id": "req-123"
}
```

## Comparison to Other Modes

| Feature | zw_embedding | Variation Selectors | Full C2PA |
|---------|--------------|---------------------|-----------|
| **Word Compatible** | ✅ Yes | ❌ Shows □ boxes | ❌ Shows glyphs |
| **Signature Size** | ~1,366 chars | ~2,000 chars | ~2,000+ chars |
| **Encoding Density** | 6 chars/byte | 1 char/byte | 1 char/byte |
| **Cryptographic Signing** | ✅ Ed25519 | ✅ Ed25519 | ✅ Ed25519 |
| **Tamper Detection** | ✅ Content hash | ✅ Content hash | ✅ Hard binding |
| **Offline Verification** | ✅ Yes | ✅ Yes | ✅ Yes |
| **C2PA Compliant** | ⚠️ Custom | ⚠️ Custom | ✅ Full spec |
| **Font Dependencies** | ✅ None | ⚠️ Some fonts | ⚠️ Some fonts |

## Use Cases

### ✅ Recommended For

1. **Microsoft Word Workflows**
   - Enterprise document signing
   - Contract authentication
   - Report provenance

2. **Cross-Platform Publishing**
   - Content that moves between Word, Google Docs, PDF
   - Email newsletters
   - Blog posts copied to multiple platforms

3. **Maximum Compatibility**
   - Unknown target platforms
   - Mobile apps
   - Legacy systems

### ⚠️ Not Recommended For

1. **C2PA Strict Compliance**
   - Use `manifest_mode: "full"` for C2PA spec compliance
   - zw_embedding is a custom format

2. **Minimal Overhead Requirements**
   - 6 chars/byte is less efficient than variation selectors (1 char/byte)
   - Use variation selectors if Word compatibility not needed

3. **Distributed Embedding**
   - zw_embedding uses single-point embedding (signature at end)
   - Use variation selectors for distributed embedding across text

## Security Considerations

### Cryptographic Strength

- **Algorithm**: Ed25519 (256-bit security)
- **Signature Size**: 64 bytes (512 bits)
- **Hash Algorithm**: SHA-256 for content hashing
- **Tamper Detection**: Any modification to text invalidates signature

### Attack Resistance

✅ **Signature Forgery**: Computationally infeasible (Ed25519)  
✅ **Content Tampering**: Detected via content hash mismatch  
✅ **Replay Attacks**: Timestamp included in signed payload  
✅ **Key Substitution**: Signer ID cryptographically bound to signature  

⚠️ **Signature Removal**: Attacker can remove signature (no protection against this)  
⚠️ **Database Compromise**: If using UUID references, DB security is critical  

### Best Practices

1. **Key Management**
   - Store private keys securely (HSM, key vault)
   - Rotate keys periodically (90-180 days)
   - Use per-organization keys (not shared)

2. **Timestamp Verification**
   - Check timestamp is within acceptable range
   - Reject signatures with future timestamps
   - Consider expiration policies

3. **Public Key Distribution**
   - Publish public keys via HTTPS
   - Use trust anchors (certificate authorities)
   - Implement key revocation mechanism

## Performance

### Encoding Performance

| Text Size | Signature Time | Signature Size |
|-----------|----------------|----------------|
| 100 chars | ~5ms | 1,366 chars |
| 1,000 chars | ~5ms | 1,366 chars |
| 10,000 chars | ~10ms | 1,366 chars |
| 100,000 chars | ~50ms | 1,366 chars |

**Note:** Signature size is constant (independent of text size)

### Verification Performance

| Operation | Time |
|-----------|------|
| Extract signature | <1ms |
| Verify Ed25519 signature | ~2ms |
| Compute content hash | ~5ms (for 10KB text) |
| **Total verification** | **~10ms** |

### Overhead Analysis

For a typical 1,000-word article (~5,000 characters):
- Signature: 1,366 ZW chars
- Overhead: 27% size increase
- Rendering: No visible impact (zero-width)

## Testing

### Automated Tests

```bash
cd enterprise_api
uv run pytest tests/test_zw_crypto.py -v
```

**Test Coverage:**
- ✅ Byte encoding/decoding roundtrip
- ✅ Signature creation and verification
- ✅ Tamper detection
- ✅ Wrong key rejection
- ✅ UUID reference mode
- ✅ Word compatibility (no variation selectors)

### Manual Testing

**Word Compatibility Test:**
1. Create signed text using zw_embedding mode
2. Copy into Microsoft Word
3. Verify no □ boxes appear
4. Copy from Word and verify signature still present

**Cross-Platform Test:**
1. Sign text with zw_embedding
2. Copy to Google Docs → verify invisible
3. Export to PDF → verify invisible
4. Copy from PDF → verify signature preserved

## Implementation Details

### Core Module

**File:** `app/utils/zw_crypto.py`

**Key Functions:**
- `create_zw_signature()` - Create cryptographic signature
- `verify_zw_signature()` - Verify signature and extract payload
- `create_uuid_reference_zw()` - Create UUID reference with signature
- `verify_uuid_reference_zw()` - Verify UUID reference
- `encode_bytes_zw()` - Encode binary data to ZW chars
- `decode_bytes_zw()` - Decode ZW chars to binary data

### Integration Points

**Embedding Service:** `app/services/embedding_service.py`
- Add `manifest_mode: "zw_embedding"` support
- Use `create_zw_signature()` instead of `UnicodeMetadata.embed_metadata()`
- Store signature metadata in database

**Verification API:** `app/api/v1/public/verify.py`
- Detect zw_embedding format via magic number
- Use `verify_zw_signature()` for verification
- Return format-specific metadata

## Migration Guide

### From Variation Selectors to zw_embedding

**Before:**
```python
embedded = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="basic"
)
```

**After:**
```python
from app.utils.zw_crypto import create_zw_signature

signature = create_zw_signature(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    metadata={"document_id": doc_id}
)
embedded = text + signature
```

### Backward Compatibility

The system supports **multiple formats simultaneously**:
- Variation selector embeddings (existing)
- zw_embedding (new)
- Full C2PA manifests (existing)

Verification API auto-detects format and uses appropriate verification method.

## Troubleshooting

### Signature Not Found

**Symptom:** `extract_zw_signature()` returns `None`

**Causes:**
- Magic number not present in text
- Signature was removed during copy/paste
- Text encoding changed (e.g., UTF-8 to ASCII conversion)

**Solution:**
- Verify magic number is present: `ZW_MAGIC_V1 in text`
- Check for ZW character stripping by platform
- Ensure UTF-8 encoding throughout pipeline

### Verification Fails

**Symptom:** `verify_zw_signature()` returns `(False, payload)`

**Causes:**
- Content was modified (hash mismatch)
- Wrong public key used for verification
- Signature corrupted during transmission

**Solution:**
- Check `payload["content_tampered"]` flag
- Verify correct public key for signer_id
- Re-sign if signature corrupted

### Visible Characters in Word

**Symptom:** Seeing □ boxes or other glyphs in Word

**Cause:** Using variation selectors instead of pure ZW chars

**Solution:**
- Verify using `zw_embedding` mode (not variation selectors)
- Run Word compatibility test: `test_word_compatibility()`
- Check signature contains only ZWSP/ZWNJ/ZWJ

## Future Enhancements

### Planned Features

1. **Distributed ZW Embedding**
   - Spread signature across multiple points in text
   - Increase resilience to partial text extraction

2. **Compression**
   - Compress payload before encoding
   - Reduce signature size by ~30-50%

3. **Multi-Signature Support**
   - Multiple signers on same document
   - Co-signing workflows

4. **Revocation**
   - Online revocation checking
   - Embedded revocation status

### Research Areas

1. **Encoding Optimization**
   - Explore base-4 or base-5 encoding for better density
   - Investigate Unicode combining marks

2. **Platform Testing**
   - Test on LibreOffice, Pages, Notion
   - Mobile app compatibility (iOS Notes, Android)
   - Email clients (Outlook, Gmail)

## References

- **Unicode Zero-Width Chars**: https://unicode.org/charts/PDF/U2000.pdf
- **Ed25519 Signature**: https://ed25519.cr.yp.to/
- **C2PA Specification**: https://c2pa.org/specifications/
- **Test Results**: `docs/ZW_VS_RENDERING_RESEARCH.md`

## Support

For questions or issues with zw_embedding mode:
1. Check test suite: `tests/test_zw_crypto.py`
2. Review research doc: `docs/ZW_VS_RENDERING_RESEARCH.md`
3. Run manual Word compatibility test
4. Contact: engineering@encypherai.com
