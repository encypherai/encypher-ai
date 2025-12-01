# C2PA Text Signing Best Practices

**Version**: 2.0
**Date**: November 2025
**Audience**: Organizations implementing C2PA text signing without prior C2PA experience

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Core Concepts](#2-core-concepts)
3. [Signing Scenarios](#3-signing-scenarios)
   - [Scenario A: Creator Signs Their Own Work](#scenario-a-creator-signs-their-own-work)
   - [Scenario B: Third Party Reviews and Approves](#scenario-b-third-party-reviews-and-approves)
   - [Scenario C: Third Party Approves Unsigned Content](#scenario-c-third-party-approves-unsigned-content)
4. [Universal Text Embedding](#4-universal-text-embedding)
   - [Why Unicode Variation Selectors Are Universal](#41-why-unicode-variation-selectors-are-universal)
   - [Full vs. Minimal Manifests](#42-full-vs-minimal-manifests)
   - [Minimal Manifest Pattern](#43-minimal-manifest-pattern-recommended)
5. [Canonicalization and Normalization](#5-canonicalization-and-normalization)
   - [NFC Normalization (Mandatory)](#52-nfc-normalization-mandatory)
   - [Hard Binding vs. Soft Binding](#53-hard-binding-vs-soft-binding)
6. [Use Case Examples](#6-use-case-examples)
   - [Message Brokers](#61-message-brokers-kafka-kinesis-pulsar)
   - [JSON Documents](#62-json-documents)
   - [XML Documents](#63-xml-documents)
   - [Database Records](#64-database-records)
7. [Tooling and Conformance Requirements](#7-tooling-and-conformance-requirements)
8. [Implementation Checklist](#8-implementation-checklist)
9. [FAQ](#9-faq)

---

## 1. Introduction

This document provides clear, practical instructions for organizations implementing C2PA (Coalition for Content Provenance and Authenticity) text signing with minimal manifests. It is written for teams who have **not** implemented any other C2PA workflows and need practical guidance.

### What is C2PA Text Signing?

C2PA text signing embeds cryptographic provenance information directly into Unicode text using invisible variation selectors. This allows:

- **Attribution**: Identify who created or approved the content
- **Integrity**: Detect if content has been modified
- **Provenance**: Track the history of content through multiple edits
- **Non-repudiation**: Cryptographic proof that a specific organization signed the content

### Key Principle: Format-Agnostic Embedding

Unlike traditional metadata approaches that rely on container-specific structures (XML attributes, JSON fields, HTTP headers), C2PA text signing uses **Unicode variation selectors** that work in:

- Plain text files (`.txt`)
- JSON documents (string values)
- XML documents (text nodes)
- Database fields (TEXT/VARCHAR columns)
- Message broker payloads (Kafka, Kinesis, Pulsar)
- API request/response bodies
- Any Unicode-capable system

**The manifest is embedded IN the text itself, not in format-specific metadata.**

### What is a "Minimal Manifest"?

A minimal C2PA manifest for text contains only the essential assertions:

| Assertion | Purpose | Required? |
|-----------|---------|-----------|
| `c2pa.actions.v1` | Records what action was taken (created, edited, approved) | **Yes** |
| `c2pa.hash.data` | Cryptographic binding to the text content (hard binding) | **Yes** |
| `c2pa.soft_binding` | URI reference to full external manifest | **Recommended** |
| Signature | COSE_Sign1 signature proving signer identity | **Yes** |

**Important Clarification**: Per C2PA 2.2 specification:
- **Hard binding is mandatory** - exactly one hard binding assertion per manifest
- **Soft binding is optional** - zero or more soft binding assertions allowed
- **Minimal manifests** (~2-5KB) with URI references enable efficient workflows

---

## 2. Core Concepts

### 2.1 The Signer's Role

**Critical Understanding**: In C2PA, the **signer** is making a statement. The signature means:

> "I, [Organization/Individual], assert that the statements in this manifest are true to the best of my knowledge."

The signer is **not** necessarily the creator. The signer is whoever is willing to cryptographically attest to the manifest's claims.

### 2.2 Trust Model

C2PA uses a **Trust Anchor** model:

1. **Signer** has a private key and certificate
2. **Certificate** is issued by a trusted Certificate Authority (CA)
3. **Validator** checks if the certificate chains to a trusted root

**For organizational signatures**: Your organization obtains a signing certificate from a CA. When you sign content, validators can verify it came from your organization.

### 2.3 Actions vs. Signatures

| Concept | What it Records | Who Performs It |
|---------|-----------------|-----------------|
| **Action** | What happened to the content (created, edited, reviewed) | The actor who performed the action |
| **Signature** | Who is attesting to the manifest's accuracy | The signer (may be different from actor) |

**Example**: A localization vendor creates Spanish metadata (`c2pa.created` action). A distributor reviews and signs it (distributor's signature). The action records the vendor's work; the signature is the distributor's attestation.

---

## 3. Signing Scenarios

### Scenario A: Creator Signs Their Own Work

**Use Case**: A localization company produces Spanish descriptive metadata and signs the file themselves.

#### Workflow

1. Localization Vendor creates Spanish metadata
2. Vendor signs with their own certificate
3. Manifest records: action=c2pa.created, signer=Vendor

#### Implementation

```json
{
  "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
  "claim_generator": "LocalizationVendor/v1.0",
  "instance_id": "uuid-1234-5678",
  "assertions": [
    {
      "label": "c2pa.actions.v1",
      "data": {
        "actions": [
          {
            "action": "c2pa.created",
            "when": "2025-11-26T10:00:00Z",
            "softwareAgent": "LocalizationTool/v2.0",
            "description": "Created Spanish descriptive metadata"
          }
        ]
      }
    },
    {
      "label": "c2pa.hash.data.v1",
      "data": {
        "hash": "<sha256-of-normalized-text>",
        "alg": "sha256",
        "exclusions": [{"start": 1234, "length": 567}]
      }
    }
  ],
  "signature": "<COSE_Sign1 with Vendor's certificate>"
}
```

#### Key Points

- **Action**: `c2pa.created` - the vendor created this content
- **Signer**: The vendor's certificate
- **Meaning**: "We, LocalizationVendor, created this Spanish metadata on this date"

---

### Scenario B: Third Party Reviews and Approves

**Use Case**: A distribution company receives localized content from a vendor, reviews it, and signs to indicate approval.

#### Workflow

1. Vendor creates and signs content (Scenario A)
2. Distributor receives signed content
3. Distributor reviews content
4. Distributor adds new manifest with:
   - action=c2pa.reviewed (or c2pa.published)
   - ingredient reference to vendor's manifest
   - Distributor's signature

#### Implementation

```json
{
  "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
  "claim_generator": "DistributorCorp/v1.0",
  "instance_id": "uuid-9999-0000",
  "assertions": [
    {
      "label": "c2pa.actions.v1",
      "data": {
        "actions": [
          {
            "action": "c2pa.opened",
            "when": "2025-11-26T14:00:00Z",
            "description": "Received for review"
          },
          {
            "action": "c2pa.published",
            "when": "2025-11-26T16:00:00Z",
            "description": "Approved for distribution"
          }
        ]
      }
    },
    {
      "label": "c2pa.ingredient.v1",
      "data": {
        "title": "Original localized content",
        "instance_id": "uuid-1234-5678",
        "relationship": "parentOf",
        "c2pa_manifest": {
          "// Complete manifest from vendor": "..."
        }
      }
    },
    {
      "label": "c2pa.hash.data.v1",
      "data": {
        "hash": "<sha256-of-normalized-text>",
        "alg": "sha256",
        "exclusions": [{"start": 2345, "length": 678}]
      }
    }
  ],
  "signature": "<COSE_Sign1 with Distributor's certificate>"
}
```

#### Key Points

- **Ingredient**: References the vendor's original manifest (preserves provenance chain)
- **Actions**: `c2pa.opened` + `c2pa.published` records the review workflow
- **Signer**: The distributor's certificate
- **Meaning**: "We, DistributorCorp, reviewed content originally created by LocalizationVendor and approve it for distribution"

---

### Scenario C: Third Party Approves Unsigned Content

**Use Case**: A distributor receives unsigned content from a vendor and signs it to indicate approval, without the vendor having signed it originally.

#### Workflow

1. Vendor creates content (NO signature)
2. Distributor receives unsigned content
3. Distributor reviews and approves
4. Distributor creates manifest with:
   - action=c2pa.created (they are first to sign)
   - OR action=c2pa.published (if they want to indicate they didn't create the content)
   - Distributor's signature

#### Implementation

```json
{
  "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
  "claim_generator": "DistributorCorp/v1.0",
  "instance_id": "uuid-aaaa-bbbb",
  "assertions": [
    {
      "label": "c2pa.actions.v1",
      "data": {
        "actions": [
          {
            "action": "c2pa.published",
            "when": "2025-11-26T16:00:00Z",
            "description": "Approved and published content created by external vendor",
            "parameters": {
              "com.yourcompany.source": "ExternalVendor",
              "com.yourcompany.approval_type": "first_signature"
            }
          }
        ]
      }
    },
    {
      "label": "c2pa.hash.data.v1",
      "data": {
        "hash": "<sha256-of-normalized-text>",
        "alg": "sha256",
        "exclusions": [{"start": 1234, "length": 567}]
      }
    }
  ],
  "signature": "<COSE_Sign1 with Distributor's certificate>"
}
```

#### Key Points

- **No ingredient reference**: There's no prior manifest to reference
- **Signer takes responsibility**: The distributor's signature means they vouch for this content
- **Use custom parameters**: Add metadata about the original source if needed
- **Meaning**: "We, DistributorCorp, are the first to cryptographically attest to this content. We received it from [source] and approve it."

---

## 4. Universal Text Embedding

### 4.1 Why Unicode Variation Selectors Are Universal

The C2PA text signing specification uses **Unicode variation selectors** (U+FE00-U+FE0F and U+E0100-U+E01EF) to embed manifests. Per the C2PA specification (`Manifests_Text.adoc`):

> "Unicode variation selectors are used because they are **specifically designed to be visually non-rendering while remaining part of the valid Unicode character set**."

#### How It Works

```
[Visible Text Content] + U+FEFF + [C2PATextManifestWrapper as variation selectors]
```

**C2PATextManifestWrapper Structure**:
```
magic:          "C2PATXT\0" (0x4332504154585400)
version:        1
manifestLength: <length in bytes>
jumbfContainer: <C2PA Manifest Store in JUMBF format>
```

Each byte is encoded as a variation selector:
- Bytes 0-15: U+FE00 to U+FE0F
- Bytes 16-255: U+E0100 to U+E01EF

#### Format-Agnostic Compatibility

This works in **any format that supports Unicode text**:

✅ Plain text files (`.txt`)
✅ JSON documents (string values)
✅ XML documents (text nodes)
✅ Database TEXT/VARCHAR columns
✅ Message broker payloads (Kafka, Kinesis, Pulsar)
✅ API request/response bodies
✅ Chat applications
✅ Email bodies
✅ Any Unicode-capable system

**The manifest is embedded IN the text itself, not in format-specific metadata.**

---

### 4.2 Full vs. Minimal Manifests

You can choose the manifest size based on your use case:

#### Option A: Full Manifest Embedded

Embed the complete manifest (including full provenance chain, all actions, ingredients):

**Pros**:
- Offline verification
- Complete provenance travels with content
- No external dependencies

**Cons**:
- ~5-50KB overhead (depending on provenance depth)
- May be significant for short messages

**Best for**: Documents, long-form content, copy-paste workflows

---

#### Option B: Minimal Manifest + External Reference (RECOMMENDED)

Embed only essential assertions and use soft binding to reference external manifest:

**Pros**:
- ~2-5KB overhead (minimal)
- Offline integrity verification (hard binding works)
- Online provenance lookup (via URI)
- Signed URL (tamper-proof)

**Cons**:
- Requires network access for full provenance
- Depends on manifest repository availability

**Best for**: Message brokers, API responses, high-volume workflows, short messages, structured documents

---

### 4.3 Minimal Manifest Pattern (RECOMMENDED)

#### Structure

```json
{
  "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
  "claim_generator": "YourOrg/v1.0",
  "instance_id": "uuid-minimal-123",
  "assertions": [
    {
      "label": "c2pa.actions.v1",
      "data": {
        "actions": [
          {
            "action": "c2pa.created",
            "when": "2025-11-30T12:00:00Z",
            "softwareAgent": "YourApp/v1.0"
          }
        ]
      }
    },
    {
      "label": "c2pa.hash.data.v1",
      "data": {
        "hash": "<sha256-of-normalized-text>",
        "alg": "sha256",
        "exclusions": [{"start": 1234, "length": 567}]
      }
    },
    {
      "label": "c2pa.soft_binding",
      "data": {
        "alg": "uri",
        "hash": "https://manifests.company.com/uuid-123.c2pa"
      }
    }
  ],
  "signature": "<COSE_Sign1>"
}
```

#### Key Components

1. **Hard Binding** (`c2pa.hash.data.v1`): Proves content integrity (works offline)
2. **Soft Binding** (`c2pa.soft_binding`): URI to full external manifest (works online)
3. **Signature**: Covers both bindings, making the URI tamper-proof

#### Benefits

- **Offline**: Hard binding verifies content hasn't been tampered with
- **Online**: Soft binding URI provides full provenance chain
- **Efficient**: ~2-5KB embedded, full manifest external
- **Secure**: Signature covers the URI (tamper-proof reference)
- **Compliant**: Fully C2PA 2.2 compliant per Section 3.2.7 (manifest externalization)

---

## 5. Canonicalization and Normalization

### 5.1 The Problem

Different systems may represent the same text differently:

- **Line endings**: `\n` vs `\r\n` vs `\r`
- **Unicode normalization**: NFC vs NFD vs NFKC vs NFKD
- **Whitespace**: Trailing spaces, tabs vs spaces

These "immaterial" differences would change the hash, causing verification failures.

---

### 5.2 NFC Normalization (MANDATORY)

Per the C2PA specification (`Manifests_Text.adoc`):

> **Both producers and consumers shall normalize text to Unicode Normalization Form C (NFC) before calculating hashes.**

#### What NFC Does

NFC (Canonical Decomposition, followed by Canonical Composition) ensures:

- Precomposed characters are used where possible (é instead of e + ´)
- Consistent byte representation across platforms

#### Universal Canonicalization Algorithm

```python
import unicodedata
import hashlib

def canonicalize_text(text: str) -> str:
    """
    Universal text canonicalization for C2PA signing.
    Works regardless of source format (XML, JSON, plain text, etc.)
    """
    # Step 1: Remove BOM if present (common in files saved from Windows)
    if text.startswith('\ufeff'):
        text = text[1:]

    # Step 2: Normalize line endings to Unix-style
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Step 3: Apply Unicode NFC normalization (MANDATORY per C2PA)
    text = unicodedata.normalize("NFC", text)

    return text

def hash_text(text: str) -> bytes:
    """Hash text content for C2PA hard binding."""
    canonical = canonicalize_text(text)
    return hashlib.sha256(canonical.encode('utf-8')).digest()
```

#### What This Algorithm Handles

| Issue | How It's Handled |
|-------|------------------|
| BOM (Byte Order Mark) | Removed |
| Line endings (`\r\n`, `\r`, `\n`) | Normalized to `\n` |
| Unicode composition (é vs e+´) | NFC normalization |
| Whitespace (spaces, tabs) | **Preserved as-is** |
| Trailing whitespace | **Preserved as-is** |

#### Why NOT Format-Specific Canonicalization

**Avoid**: XML C14N or JSON JCS before hashing

**Reason**: Breaks cross-format portability. If you hash canonicalized XML, verification fails when text is copied to JSON or plain text.

**Default recommendation**: Use NFC normalization alone for maximum portability.

---

### 5.3 Hard Binding vs. Soft Binding

#### Hard Binding (MANDATORY)

**What it is**: A cryptographic hash of the content that proves the content hasn't been modified.

**Requirement**: Exactly **one** hard binding is required per manifest. For text, this is `c2pa.hash.data`.

**What it proves**: "This exact text (byte-for-byte, after NFC normalization) is what was signed."

#### Soft Binding (OPTIONAL)

**What it is**: A perceptual fingerprint, watermark, or **URI reference** that can identify content or locate manifests even after modifications.

**Requirement**: Zero or more soft bindings allowed per manifest.

**What it's for**:
1. **Manifest recovery**: If the manifest is stripped, a soft binding can help locate the original manifest in a repository
2. **Derived content matching**: Identify content that's been transcoded, resized, or reformatted
3. **URI references**: Point to full external manifests (recommended for minimal manifests)

**When to use soft bindings**:
- ✅ You want to embed minimal manifests with URI references to full manifests (recommended)
- ✅ You have a manifest repository and want to enable lookup
- ✅ Content may be reformatted/transcoded and you want to track it

**When you DON'T need soft bindings**:
- ❌ Full manifests already embedded
- ❌ No external manifest repository

---

## 6. Use Case Examples

### 6.1 Message Brokers (Kafka, Kinesis, Pulsar)

#### Use Case

Log-based message brokers where:
- Full revision history is a fundamental feature (append-only logs)
- Minimal overhead is critical (high-volume streams)
- Cross-format portability is required (messages may be exported/transformed)

#### Pattern

Embed minimal manifest directly in message payload using Unicode variation selectors.

#### Example: Kafka Message

```python
# Producer
message = "User alice@example.com logged in at 2025-11-30T12:00:00Z"
minimal_manifest = create_minimal_manifest(
    content=message,
    action="c2pa.created",
    external_manifest_uri="https://manifests.company.com/msg-uuid-123.c2pa"
)
signed_message = embed_manifest(message, minimal_manifest)
producer.send(topic="audit_log", value=signed_message)

# Consumer
message = consumer.poll()
content, manifest = extract_manifest(message)
if verify_signature(manifest) and verify_hard_binding(content, manifest):
    # Content is authentic and unmodified
    full_manifest_uri = manifest['assertions']['c2pa.soft_binding']['hash']
    # Fetch full provenance on-demand if needed
```

#### Benefits

- Provenance embedded in append-only log (tamper-evident)
- No separate manifest storage required
- Hard binding works offline
- Full provenance available on-demand (URI)
- ~2-5KB overhead per message

---

### 6.2 JSON Documents

#### Use Case

Schema-validated JSON documents where:
- Signature must not distort the document structure
- Document must remain valid JSON
- Cross-format portability required (JSON → XML → database → plain text)

#### Pattern

Manifest is embedded **in the text content itself** via Unicode variation selectors, NOT as a JSON field.

#### Example

```json
{
  "content_id": "spanish-ad-scene-1",
  "description": "María entra en la habitación y observa la escena<U+FEFF><variation-selectors>",
  "language": "es-ES",
  "duration_ms": 4500
}
```

**Key points**:
- The manifest is **part of the string value** for `description`
- No JSON schema changes required
- Copy-paste to a `.txt` file preserves the manifest
- Paste into a database field preserves the manifest
- Variation selectors are invisible when rendered

#### Implementation

```python
# Signing
description = "María entra en la habitación y observa la escena"
minimal_manifest = create_minimal_manifest(
    content=description,
    action="c2pa.created",
    external_manifest_uri="https://manifests.company.com/doc-uuid-456.c2pa"
)
signed_description = embed_manifest(description, minimal_manifest)

json_doc = {
    "content_id": "spanish-ad-scene-1",
    "description": signed_description,  # Contains invisible manifest
    "language": "es-ES"
}

# Verification
json_doc = json.loads(response.text)
content, manifest = extract_manifest(json_doc["description"])
if verify_signature(manifest) and verify_hard_binding(content, manifest):
    # Description is authentic
```

---

### 6.3 XML Documents

#### Use Case

Schema-validated XML documents where:
- Signature must not distort the document structure
- Document must remain valid XML
- Cross-format portability required

#### Pattern

Manifest is embedded **in the text node itself** via Unicode variation selectors, NOT as XML attributes or elements.

#### Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<descriptive-metadata>
  <content id="scene-1" lang="es">
    María entra en la habitación y observa la escena<U+FEFF><variation-selectors>
  </content>
  <timestamp>2025-11-30T12:00:00Z</timestamp>
</descriptive-metadata>
```

**Key points**:
- The manifest is **part of the text node**
- No XML schema changes required
- Remains valid XML (variation selectors are valid Unicode)
- Copy-paste preserves manifest

---

### 6.4 Database Records

#### Use Case

Audit logs, content metadata, or any text stored in database TEXT/VARCHAR columns.

#### Pattern

Manifest is embedded **in the text value itself** via Unicode variation selectors.

#### Example

```sql
-- Insert signed content
INSERT INTO audit_log (timestamp, event_description, user_id) VALUES (
  '2025-11-30 12:00:00',
  'User alice@example.com logged in from IP 192.0.2.1<U+FEFF><variation-selectors>',
  'alice'
);

-- Query and verify
SELECT event_description FROM audit_log WHERE user_id = 'alice';
-- Application extracts manifest and verifies signature
```

**Key points**:
- The manifest is **part of the VARCHAR/TEXT column**
- No schema changes required
- Survives database export/import
- Works with any database (PostgreSQL, MySQL, SQLite, etc.)

---

## 7. Tooling and Conformance Requirements

### 7.1 Can Non-Conforming Tools Be Used?

**Short Answer**: Yes, with caveats.

**Long Answer**: The C2PA specification distinguishes between:

1. **Conforming Products**: Listed on the [C2PA Conforming Products List](https://c2pa.org/conformance/)
2. **Non-Conforming Tools**: Any tool that implements C2PA but isn't on the list

### 7.2 Organizational Signatures vs. Product Signatures

| Aspect | Product Signature | Organizational Signature |
|--------|-------------------|--------------------------|
| **Certificate Subject** | "Adobe Photoshop" | "Acme Corporation" |
| **What it proves** | This tool created the manifest | This organization vouches for the manifest |
| **Conformance requirement** | Tool should be conforming | Tool conformance less critical |

**Your Goal**: Organizational signature → Tool conformance is secondary.

### 7.3 Requirements for Non-Conforming Tools

If using a non-conforming tool for organizational signatures:

1. **Implement the specification correctly**
   - Follow `C2PATextManifestWrapper` structure exactly
   - Use correct byte-to-variation-selector mapping
   - Apply NFC normalization before hashing
   - Use SHA-256 for hashes
   - Use COSE_Sign1 for signatures

2. **Use proper certificates**
   - Obtain certificates from a recognized CA
   - Certificate should identify your organization
   - Include proper Extended Key Usage (EKU)

3. **Validate your implementation**
   - Test against reference implementations
   - Verify manifests can be read by conforming validators
   - Document any deviations

---

## 8. Implementation Checklist

### 8.1 Before You Start

- [ ] Obtain organizational signing certificate from a CA
- [ ] Set up secure key storage (HSM recommended for production)
- [ ] Set up manifest repository (if using minimal manifests with URI references)
- [ ] Document your signing policy (who can sign, what review is required)

### 8.2 Technical Requirements

- [ ] Implement NFC normalization before all hashing
- [ ] Use SHA-256 for content hashes
- [ ] Use COSE_Sign1 for signatures (Ed25519 or ECDSA P-256 recommended)
- [ ] Follow `C2PATextManifestWrapper` structure exactly
- [ ] Calculate exclusion regions correctly for hard binding
- [ ] Implement byte-to-variation-selector encoding correctly

### 8.3 Minimal Manifest Pattern

- [ ] Implement minimal manifest creation (actions + hard binding + soft binding URI + signature)
- [ ] Set up manifest repository with HTTPS access
- [ ] Serve external manifests with `Content-Type: application/c2pa`
- [ ] Implement URI signing (soft binding URI covered by signature)

### 8.4 Validation

- [ ] Test manifest extraction from Unicode variation selectors
- [ ] Verify signature validates against certificate
- [ ] Verify hard binding (content hash) matches
- [ ] Verify soft binding URI is signed (tamper-proof)
- [ ] Test with modified content (should fail verification)
- [ ] Test cross-format portability (JSON → XML → plain text)

---

## 9. FAQ

### Q: Do I need to be on the C2PA Conforming Products List?

**A**: No, not for organizational signatures. The conforming products list is primarily for tools that want to advertise C2PA compliance. For organizational signatures, what matters is:
1. Your implementation follows the specification
2. Your certificate identifies your organization
3. Validators can verify your signatures

### Q: What if the original creator didn't sign the content?

**A**: You can still sign it (Scenario C). Your signature means "I, [Organization], vouch for this content." Use appropriate actions (`c2pa.published` rather than `c2pa.created`) to make this clear.

### Q: Can I sign content without embedding the manifest?

**A**: Yes, but we recommend the **minimal manifest + URI** pattern instead. This gives you:
- Offline integrity verification (hard binding)
- Tamper-proof URL (signed soft binding)
- Full provenance available online (external manifest)

Pure external manifests (HTTP `Link` headers, XMP references) lose portability when content is copied.

### Q: Why use Unicode variation selectors instead of JSON/XML metadata?

**A**: Format-agnostic portability. Unicode variation selectors work everywhere:
- ✅ Copy-paste between formats (JSON → XML → plain text)
- ✅ Database storage (TEXT/VARCHAR columns)
- ✅ Message brokers (Kafka, Kinesis, Pulsar)
- ✅ No schema changes required

JSON/XML metadata breaks when content is copied to other formats.

### Q: What's the overhead of minimal manifests?

**A**: ~2-5KB embedded using Unicode variation selectors. This includes:
- Hard binding (content hash)
- Soft binding (URI to full manifest)
- Signature
- Minimal action history

Full manifests with provenance chains: ~5-50KB depending on depth.

### Q: How do I handle multiple signers?

**A**: Use the ingredient system. Each signer creates a new manifest that references the previous manifest as an ingredient:

```
Vendor signs → Manifest A (embedded minimal + URI to full A)
Distributor signs → Manifest B (embedded minimal + URI to full B, ingredient: A)
Publisher signs → Manifest C (embedded minimal + URI to full C, ingredient: B)
```

Full provenance chains stored externally, minimal manifests embedded.

### Q: What timestamp should I use?

**A**: Use the actual time of signing in ISO 8601 format with UTC timezone:
```
2025-11-26T16:30:00Z
```

For legal evidence, consider adding an RFC 3161 timestamp from a Timestamp Authority (TSA).

### Q: How does this relate to ETSI XAdES/JAdES?

**A**: C2PA minimal manifests with URI references are conceptually similar to ETSI's detached signatures (XAdES-B-T, JAdES-B-T):

| Feature | ETSI XAdES/JAdES | C2PA Minimal Manifest |
|---------|------------------|----------------------|
| **Detached signature** | Separate XML/JSON file | Embedded via Unicode VS |
| **Content binding** | Hash reference | Hard binding (hash) |
| **External manifest** | Separate file | URI via soft binding |
| **Timestamp** | RFC 3161 TSA | Optional TSA or action timestamp |
| **Format-agnostic** | ❌ XML/JSON specific | ✅ Unicode-based |

C2PA adds format-agnostic portability via Unicode variation selectors.

---

## References

- [C2PA Technical Specification 2.2](https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)
- [C2PA Implementation Guidance](https://c2pa.org/specifications/specifications/2.2/guidance/Guidance.html)
- [C2PA Manifests_Text Specification](https://c2pa.org/specifications/specifications/2.2/specs/Manifests_Text.html)
- [Unicode Normalization Forms (UAX #15)](https://www.unicode.org/reports/tr15/)
- [ETSI TS 119 182-1 (JAdES)](https://www.etsi.org/deliver/etsi_ts/119100_119199/11918201/01.01.01_60/ts_11918201v010101p.pdf)
- [RFC 3161 - Time-Stamp Protocol (TSP)](https://datatracker.ietf.org/doc/html/rfc3161)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | November 2025 | Initial release |
| 2.0 | November 2025 | Major revision: Universal text embedding via Unicode variation selectors, minimal manifest + URI pattern, message broker/database/API examples, format-agnostic portability emphasis |
