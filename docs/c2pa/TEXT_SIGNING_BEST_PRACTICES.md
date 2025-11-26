# C2PA Text Signing Best Practices

**Version**: 1.0  
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
4. [Canonicalization and Normalization](#4-canonicalization-and-normalization)
   - [Recommended Approach: NFC Only](#43-recommended-approach-nfc-only)
   - [Hard Binding vs. Soft Binding](#46-hard-binding-vs-soft-binding-whats-actually-required)
   - [External Manifests](#47-external-manifests-a-lighter-weight-alternative)
5. [Tooling and Conformance Requirements](#5-tooling-and-conformance-requirements)
6. [Implementation Checklist](#6-implementation-checklist)
7. [FAQ](#7-faq)

---

## 1. Introduction

This document provides painfully clear instructions for organizations implementing C2PA (Coalition for Content Provenance and Authenticity) text signing with minimal manifests. It is written for teams who have **not** implemented any other C2PA workflows and need practical guidance.

### What is C2PA Text Signing?

C2PA text signing embeds cryptographic provenance information directly into Unicode text using invisible variation selectors. This allows:

- **Attribution**: Identify who created or approved the content
- **Integrity**: Detect if content has been modified
- **Provenance**: Track the history of content through multiple edits

### What is a "Minimal Manifest"?

A minimal C2PA manifest for text contains only the essential assertions:

| Assertion | Purpose | Required? |
|-----------|---------|-----------|
| `c2pa.actions.v1` | Records what action was taken (created, edited, approved) | **Yes** |
| `c2pa.hash.data` | Cryptographic binding to the text content (hard binding) | **Yes** |
| `c2pa.soft-binding` | Perceptual hash or watermark for content recovery | **Optional** |
| Signature | COSE_Sign1 signature proving signer identity | **Yes** |

**Important Clarification**: Per C2PA 2.2 specification:
- **Hard binding is mandatory** - exactly one hard binding assertion per manifest
- **Soft binding is optional** - zero or more soft binding assertions allowed
- Soft bindings serve a *different purpose* than hard bindings (see Section 4.5)

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

#### Alternative: Custom "Reviewed" Action

If you need to explicitly indicate review/approval, you can use a custom action:

```json
{
  "action": "com.yourcompany.reviewed",
  "when": "2025-11-26T15:00:00Z",
  "description": "Quality review completed and approved"
}
```

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

#### Implementation Option 1: Distributor as "First Signer"

Use when the distributor is taking full responsibility:

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
            "action": "c2pa.created",
            "when": "2025-11-26T10:00:00Z",
            "description": "Content received from external vendor and approved",
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

#### Implementation Option 2: Explicit "Published" Action

Use when you want to clearly indicate you're publishing someone else's work:

```json
{
  "label": "c2pa.actions.v1",
  "data": {
    "actions": [
      {
        "action": "c2pa.published",
        "when": "2025-11-26T16:00:00Z",
        "description": "Approved and published content created by external vendor"
      }
    ]
  }
}
```

#### Key Points

- **No ingredient reference**: There's no prior manifest to reference
- **Signer takes responsibility**: The distributor's signature means they vouch for this content
- **Use custom parameters**: Add metadata about the original source if needed
- **Meaning**: "We, DistributorCorp, are the first to cryptographically attest to this content. We received it from [source] and approve it."

#### Important Consideration

When signing unsigned content, the signer is making a stronger statement because there's no prior provenance. Consider:

1. **Document your review process** in the action description
2. **Add custom assertions** for audit trail (who reviewed, when, what criteria)
3. **Keep records** of the original source outside the manifest

---

## 4. Canonicalization and Normalization

### 4.1 The Problem

Different systems may represent the same text differently:

- **Line endings**: `\n` vs `\r\n` vs `\r`
- **Unicode normalization**: NFC vs NFD vs NFKC vs NFKD
- **Whitespace**: Trailing spaces, tabs vs spaces
- **XML/JSON**: Attribute ordering, whitespace in tags

These "immaterial" differences would change the hash, causing verification failures.

### 4.2 C2PA's Solution: NFC Normalization

Per the C2PA specification (`Manifests_Text.adoc`):

> **Both producers and consumers shall normalize text to Unicode Normalization Form C (NFC) before calculating hashes.**

#### What NFC Does

NFC (Canonical Decomposition, followed by Canonical Composition) ensures:

- Precomposed characters are used where possible (é instead of e + ´)
- Consistent byte representation across platforms

#### Implementation

```python
import unicodedata

def normalize_for_hashing(text: str) -> bytes:
    """Normalize text to NFC and encode as UTF-8 for hashing."""
    normalized = unicodedata.normalize("NFC", text)
    return normalized.encode("utf-8")
```

### 4.3 Recommended Approach: NFC Only

#### Why One Algorithm for All Formats?

Text content is portable. The same text might be:
- Created in an XML file
- Copied into a Word document
- Pasted into a database field
- Sent via a chat application
- Stored in a plain `.txt` file

If you use format-specific canonicalization (like XML C14N or JSON JCS) before hashing, **verification will fail** when that text is copied into a different container. The hash was computed on canonicalized XML, but the validator only has plain text.

**Therefore, we recommend using NFC normalization alone for all text formats.**

#### The Universal Canonicalization Algorithm

```python
import unicodedata

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
    import hashlib
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

#### What This Algorithm Does NOT Handle

| Issue | Why We Don't Handle It |
|-------|------------------------|
| XML attribute ordering | Would break cross-format verification |
| JSON key ordering | Would break cross-format verification |
| Insignificant whitespace in XML/JSON | Would break cross-format verification |
| Pretty-printing differences | Would break cross-format verification |

**This is intentional.** If the text content changes (even "insignificantly"), the hash should change. The signer is attesting to *this exact text*.

### 4.4 Why We Don't Recommend Format-Specific Canonicalization

Some implementations use XML C14N or JSON JCS before hashing. **We recommend against this** because it breaks cross-format portability.

#### Example: Why JCS Breaks Portability

```
Original JSON:     {"name": "Alice", "age": 30}
After JCS:         {"age":30,"name":"Alice"}     ← keys reordered, whitespace removed
Hash computed on:  {"age":30,"name":"Alice"}
```

Now someone copies the original JSON text into a `.txt` file:
```
Text in .txt:      {"name": "Alice", "age": 30}  ← original formatting preserved
Hash computed on:  {"name": "Alice", "age": 30}  ← DIFFERENT from JCS version
Result:            ❌ VERIFICATION FAILS
```

#### With NFC-Only (Our Recommendation)

```
Original JSON:     {"name": "Alice", "age": 30}
After NFC:         {"name": "Alice", "age": 30}  ← unchanged (already NFC)
Hash computed on:  {"name": "Alice", "age": 30}
```

Copy to `.txt`:
```
Text in .txt:      {"name": "Alice", "age": 30}  ← same text
After NFC:         {"name": "Alice", "age": 30}  ← same result
Result:            ✅ VERIFICATION SUCCEEDS
```

#### When Format-Specific Canonicalization Is Acceptable

Only use C14N/JCS if **all** of these are true:

1. Text will **never** be copied to another format
2. All validators use the **same** canonicalization
3. You're signing the **structure**, not just the text content
4. You accept that verification fails if text is reformatted

**This is rare.** For most text signing use cases, stick with NFC only.

### 4.5 Best Practice Summary

| Scenario | Canonicalization | Rationale |
|----------|------------------|-----------|
| **General text signing** | NFC only | Cross-format portability |
| **Copy-paste workflows** | NFC only | Content may change containers |
| **Database storage** | NFC only | No format context |
| **API/chat transmission** | NFC only | Format-agnostic |
| **Closed XML ecosystem** | C14N + NFC | Only if you accept the trade-off |
| **Closed JSON ecosystem** | JCS + NFC | Only if you accept the trade-off |

**Default recommendation: Use NFC normalization alone for maximum portability.**

### 4.6 Hard Binding vs. Soft Binding: What's Actually Required?

This is a common source of confusion. Let's clarify based on the C2PA 2.2 specification:

#### Hard Binding (MANDATORY)

**What it is**: A cryptographic hash of the content that proves the content hasn't been modified.

**Requirement**: Per Section 9.1 of C2PA 2.2:
> "A single manifest shall not contain more than one assertion defining a hard binding"

This means exactly **one** hard binding is required. For text, this is `c2pa.hash.data`.

**What it proves**: "This exact text (byte-for-byte, after NFC normalization) is what was signed."

#### Soft Binding (OPTIONAL)

**What it is**: A perceptual fingerprint or watermark that can identify content even after modifications.

**Requirement**: Per Section 9.1 of C2PA 2.2:
> "[A manifest] may contain zero or more assertions defining soft bindings."

Soft bindings are **completely optional**.

**What it's for**:
1. **Content recovery**: If the manifest is stripped, a soft binding can help locate the original manifest in a repository
2. **Derived content matching**: Identify content that's been transcoded, resized, or reformatted
3. **Watermark-based lookup**: Invisible watermarks that survive content transformations

**When to use soft bindings**:
- You have a manifest repository and want to enable lookup
- Content may be reformatted/transcoded and you want to track it
- You're implementing durable content credentials

**When you DON'T need soft bindings**:
- Simple text signing where content won't be transformed
- Embedded manifests that travel with the content
- Workflows where exact byte-matching is sufficient

#### JUMBF and Hashing

**Question**: "Doesn't JUMBF contain hashes in its headers?"

**Answer**: No, not in the way you might think. JUMBF (ISO 19566-5) is a container format. The C2PA manifest is stored *inside* JUMBF, but:
- JUMBF itself doesn't provide content binding
- The `c2pa.hash.data` assertion inside the manifest provides the hard binding
- The COSE_Sign1 signature covers the claim (which references the assertions by hash)

The chain of trust is:
```
Signature → covers → Claim → references → Assertions (by hash) → includes → c2pa.hash.data → hashes → Content
```

### 4.7 External Manifests: A Lighter-Weight Alternative

**Question**: "Can I use a URL reference to an external manifest instead of embedding?"

**Answer**: Yes! This is explicitly supported by C2PA 2.2 and is **fully compliant**.

#### When to Use External Manifests

Per Section 11.4 of C2PA 2.2, external manifests are appropriate when:

1. **Embedding is not technically possible** (e.g., plain `.txt` files without Unicode support)
2. **Manifest is larger than the content** (common for text with rich provenance chains)
3. **Content should not be modified** (e.g., archival documents)
4. **Adding provenance to pre-existing assets**

#### How External Manifests Work

1. **Store the manifest** in a manifest repository accessible via HTTP
2. **Reference it** via:
   - XMP `dcterms:provenance` property (if the format supports XMP)
   - HTTP `Link` header when serving the content
   - Out-of-band communication (e.g., database lookup by content hash)

3. **Serve with correct MIME type**: `application/c2pa`

#### Example: HTTP Link Header

When serving text content, include:
```http
Link: <https://manifests.example.com/abc123.c2pa>; rel="provenance"
Content-Type: text/plain
```

#### Example: XMP Reference

If your text format supports XMP metadata:
```xml
<rdf:Description xmlns:dcterms="http://purl.org/dc/terms/">
  <dcterms:provenance>https://manifests.example.com/abc123.c2pa</dcterms:provenance>
</rdf:Description>
```

#### Trade-offs: Embedded vs. External

| Aspect | Embedded (Unicode VS) | External (URL Reference) |
|--------|----------------------|--------------------------|
| **Overhead** | ~2-10KB per document | ~100 bytes (URL only) |
| **Portability** | Manifest travels with content | Requires network access |
| **Copy-paste** | Works across platforms | May lose reference |
| **Verification** | Offline capable | Requires manifest fetch |
| **Best for** | Documents shared widely | Internal systems, APIs |

#### Hybrid Approach

You can use both:
1. **Embed a minimal manifest** with just the hard binding and signature
2. **Reference an external manifest** with full provenance chain, ingredients, etc.

This gives you the best of both worlds: offline verification of integrity, with rich provenance available when online.

---

## 5. Tooling and Conformance Requirements

### 5.1 Can Non-Conforming Tools Be Used?

**Short Answer**: Yes, with caveats.

**Long Answer**: The C2PA specification distinguishes between:

1. **Conforming Products**: Listed on the [C2PA Conforming Products List](https://c2pa.org/conformance/)
2. **Non-Conforming Tools**: Any tool that implements C2PA but isn't on the list

### 5.2 What the Specification Says

From the C2PA Implementation Guidance:

> "The Signer of the C2PA Manifest needs to consider if they wish to be responsible for ensuring that the user generated text is something they are willing to take responsibility for, since that is a key role of the signer."

The key insight: **The signature identifies the organization, not the tool.**

### 5.3 Organizational Signatures vs. Product Signatures

| Aspect | Product Signature | Organizational Signature |
|--------|-------------------|--------------------------|
| **Certificate Subject** | "Adobe Photoshop" | "Acme Corporation" |
| **What it proves** | This tool created the manifest | This organization vouches for the manifest |
| **Conformance requirement** | Tool should be conforming | Tool conformance less critical |

**Your Goal**: Organizational signature → Tool conformance is secondary.

### 5.4 Requirements for Non-Conforming Tools

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

4. **Accept the responsibility**
   - Your organization is vouching for the content
   - If the tool has bugs, your signature is still on the content

### 5.5 Practical Recommendation

**For Organizational Signatures:**

1. Use any tool that correctly implements C2PA
2. Obtain an organizational certificate
3. Sign with your organization's identity
4. Validators will see: "Signed by: Acme Corporation"

The tool used is recorded in `claim_generator` but is secondary to the organizational identity in the signature.

### 5.6 What Gets Recorded

```json
{
  "claim_generator": "Encypher Enterprise API/v1.0",
  "signature": {
    "certificate": {
      "subject": "CN=Acme Corporation, O=Acme Corp, C=US",
      "issuer": "CN=DigiCert, O=DigiCert Inc, C=US"
    }
  }
}
```

- **claim_generator**: Records the tool (informational)
- **signature.certificate.subject**: Records the organization (authoritative)

Validators care about the certificate subject, not the claim_generator.

---

## 6. Implementation Checklist

### 6.1 Before You Start

- [ ] Obtain organizational signing certificate from a CA
- [ ] Decide on canonicalization approach (plain NFC vs. format-specific)
- [ ] Document your signing policy (who can sign, what review is required)
- [ ] Set up secure key storage (HSM recommended for production)

### 6.2 For Each Signing Scenario

#### Scenario A: Creator Signs Own Work

- [ ] Record `c2pa.created` action with timestamp
- [ ] Include creator information in action parameters
- [ ] Sign with creator's organizational certificate
- [ ] Store manifest for future reference

#### Scenario B: Third Party Reviews Signed Content

- [ ] Extract and validate incoming manifest
- [ ] Create new manifest with `c2pa.opened` + `c2pa.published` actions
- [ ] Include original manifest as ingredient with `parentOf` relationship
- [ ] Sign with reviewer's organizational certificate
- [ ] Preserve provenance chain

#### Scenario C: Third Party Signs Unsigned Content

- [ ] Document source of content in action description
- [ ] Use `c2pa.created` or `c2pa.published` action as appropriate
- [ ] Add custom parameters for audit trail
- [ ] Sign with reviewer's organizational certificate
- [ ] Keep external records of content source

### 6.3 Technical Requirements

- [ ] Implement NFC normalization before all hashing
- [ ] Use SHA-256 for content and soft binding hashes
- [ ] Use COSE_Sign1 for signatures (Ed25519 or ECDSA P-256 recommended)
- [ ] Follow `C2PATextManifestWrapper` structure exactly
- [ ] Calculate exclusion regions correctly for hard binding
- [ ] Include all mandatory assertions

### 6.4 Validation

- [ ] Test manifest extraction and verification
- [ ] Verify signature validates against certificate
- [ ] Verify hard binding (content hash) matches
- [ ] Verify soft binding (manifest hash) matches
- [ ] Test with modified content (should fail verification)

---

## 7. FAQ

### Q: Do I need to be on the C2PA Conforming Products List?

**A**: No, not for organizational signatures. The conforming products list is primarily for tools that want to advertise C2PA compliance. For organizational signatures, what matters is:
1. Your implementation follows the specification
2. Your certificate identifies your organization
3. Validators can verify your signatures

### Q: What if the original creator didn't sign the content?

**A**: You can still sign it (Scenario C). Your signature means "I, [Organization], vouch for this content." You're not claiming to have created it—you're claiming to have reviewed and approved it. Use appropriate actions (`c2pa.published` rather than `c2pa.created`) to make this clear.

### Q: How do I handle content that's been reformatted?

**A**: This is the canonicalization problem. If content may be reformatted between signing and verification:
1. **For plain text**: NFC normalization handles most cases
2. **For XML/JSON**: Consider format-specific canonicalization before NFC
3. **Document your approach**: So validators know what to expect

### Q: Can I sign content without embedding the manifest?

**A**: Yes! C2PA explicitly supports external manifests (see Section 4.6). This is fully compliant and useful when:
1. Embedding would add too much overhead
2. Content shouldn't be modified
3. You're adding provenance to existing assets

Reference the external manifest via HTTP `Link` header or XMP `dcterms:provenance`.

### Q: What's the difference between hard binding and soft binding?

**A**: 
- **Hard binding** (`c2pa.hash.data`): Cryptographic hash of the content. **Required** (exactly one per manifest). Proves the exact bytes haven't changed.
- **Soft binding** (`c2pa.soft-binding`): Perceptual fingerprint or watermark. **Optional** (zero or more). Used for content recovery and matching derived content.

**Only hard binding is required.** Soft binding is for advanced use cases like manifest recovery from repositories. See Section 4.5 for details.

### Q: How do I handle multiple signers?

**A**: Use the ingredient system. Each signer creates a new manifest that references the previous manifest as an ingredient. This creates a provenance chain:

```
Vendor signs → Manifest A
Distributor signs → Manifest B (ingredient: Manifest A)
Publisher signs → Manifest C (ingredient: Manifest B)
```

### Q: What timestamp should I use?

**A**: Use the actual time of signing in ISO 8601 format with UTC timezone:
```
2025-11-26T16:30:00Z
```

For legal evidence, consider adding an RFC 3161 timestamp from a Timestamp Authority (TSA).

### Q: How do I revoke a signature?

**A**: C2PA doesn't have a built-in revocation mechanism for individual manifests. Options:
1. **Certificate revocation**: Revoke the signing certificate (affects all content signed with it)
2. **Manifest repository**: If using a manifest repository, remove the manifest
3. **New manifest**: Sign a new version with a `c2pa.redacted` action

---

## References

- [C2PA Technical Specification 2.2](https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)
- [C2PA Implementation Guidance](https://c2pa.org/specifications/specifications/2.2/guidance/Guidance.html)
- [C2PA UX Recommendations](https://c2pa.org/specifications/specifications/2.0/ux/UX_Recommendations.html)
- [Unicode Normalization Forms (UAX #15)](https://www.unicode.org/reports/tr15/)
- [RFC 8785 - JSON Canonicalization Scheme](https://datatracker.ietf.org/doc/html/rfc8785)
- [Canonical XML 1.1](https://www.w3.org/TR/xml-c14n11/)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | November 2025 | Initial release |
