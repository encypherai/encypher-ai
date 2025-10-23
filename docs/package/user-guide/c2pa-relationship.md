# C2PA Integration for Text Content

The EncypherAI SDK provides a robust, C2PA-compliant solution for embedding provenance and authenticity metadata directly into plain text. While the official C2PA standard primarily focuses on container-based media files (like JPEG or MP4), our SDK extends these principles to the text domain, which traditionally lacks a standard embedding mechanism.

> Note: Timestamps are optional in C2PA text embeddings. When omitted, C2PA action assertions that normally include a `when` field (e.g., `c2pa.created`, `c2pa.watermarked`) will simply omit it.

## Our Approach: C2PA Compliance via Unicode

We enable C2PA compliance for text by using Unicode variation selectors as a **transport layer**. This means:

1.  **Standard C2PA Manifest**: You create a standard C2PA manifest, complete with assertions, cryptographic hashes, and digital signatures, as you would for any other media type.
2.  **COSE Sign1 Structure**: The manifest is packaged into a `COSE_Sign1` object, the standard cryptographic container used in C2PA.
3.  **Unicode Embedding**: Instead of injecting this `COSE_Sign1` object into a file container, our SDK serializes it and embeds the resulting bytes invisibly into the text itself using non-printing Unicode characters.

This approach makes the text itself the carrier of its own C2PA provenance, ensuring the metadata travels with the content wherever it's copied or published.

## Key C2PA Features Supported

Our implementation fully supports the core security features of the C2PA standard:

-   **Digital Signatures (COSE)**: Manifests are signed using Ed25519 keys within a `COSE_Sign1` structure, ensuring authenticity and integrity.
-   **Hard Binding**: A cryptographic hash of the original, clean text content is included in the manifest. This creates a tamper-evident seal, proving the text has not been altered.
-   **Soft Binding**: A hash of the manifest's assertions is also included, preventing claims from being added, removed, or modified after signing.
-   **X.509 Certificate Chains**: You can provide a certificate chain along with the signature, allowing verifiers to trace the key's authenticity back to a trusted root Certificate Authority (CA).

## Practical Example: Embedding a C2PA Manifest

This self-contained example demonstrates the end-to-end workflow: creating a manifest, embedding it, and verifying it.

```python
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import compute_normalized_hash

def run_c2pa_text_demo():
    """Demonstrates embedding and verifying a C2PA manifest in text."""

    # 1. Generate a key pair for signing
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "com.example.news-outlet"

    # 2. Define the clean text content
    original_text = "The new AI regulations will take effect next quarter, according to sources."

    # 3. Create a C2PA manifest dictionary
    # This includes a hard-binding content hash to protect against tampering.
    hash_result = compute_normalized_hash(original_text)

    c2pa_manifest = {
        "claim_generator": "EncypherAI-SDK/1.1.0",
        "assertions": [
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "author": {
                        "@type": "Organization",
                        "name": "Example News Co."
                    },
                },
            },
            {
                "label": "c2pa.hash.data.v1",
                "data": {
                    "hash": hash_result.hexdigest,
                    "alg": "sha256",
                },
                "kind": "ContentHash",
            },
        ],
    }

    # 4. Embed the manifest into the text
    # The `c2pa` format handles all COSE signing and CBOR encoding internally.
    embedded_text = UnicodeMetadata.embed_metadata(
        text=original_text,
        private_key=private_key,
        signer_id=signer_id,
        c2pa_manifest=c2pa_manifest,
    )

    print(f"Original text length: {len(original_text)}")
    print(f"Embedded text length: {len(embedded_text)}")
    print("--- Text with embedded C2PA manifest ---")
    print(embedded_text)
    print("-----------------------------------------")

    # 5. Verify the embedded manifest
    # The public key resolver function allows the verifier to look up the correct
    # public key based on the signer_id found in the manifest.
    def public_key_resolver(kid):
        if kid == signer_id:
            return public_key
        return None

    is_verified, extracted_id, payload = UnicodeMetadata.verify_metadata(
        text=embedded_text,
        public_key_resolver=public_key_resolver,
    )

    print(f"\nVerification result: {'SUCCESS' if is_verified else 'FAILURE'}")
    print(f"Extracted Signer ID: {extracted_id}")

    if payload:
        print("Extracted and Verified Payload:")
        # The payload contains the original manifest assertions
        for assertion in payload.assertions:
            print(f"- Assertion Label: {assertion.label}")

    # --- Tampering Demo ---
    print("\n--- Demonstrating Tamper Detection ---")
    tampered_text = embedded_text.replace("next quarter", "immediately")

    is_verified_tampered, _, _ = UnicodeMetadata.verify_metadata(
        text=tampered_text, public_key_resolver=public_key_resolver
    )

    print(f"Verification of tampered text: {'SUCCESS' if is_verified_tampered else 'FAILURE'}")
    assert not is_verified_tampered, "Tamper detection failed!"
    print("Tampering was successfully detected, as expected.")

if __name__ == "__main__":
    run_c2pa_text_demo()
```

### Running the Example

When you run this script, you will see:

1.  The original text is successfully embedded with a C2PA manifest.
2.  The `verify_metadata` function successfully authenticates the signature and validates the content hash, confirming the text is genuine.
3.  When a single word of the text is changed, the verification fails, demonstrating the power of the hard-binding content hash.

This workflow provides a powerful tool for establishing trust and transparency in AI-generated text and other plain-text content.
