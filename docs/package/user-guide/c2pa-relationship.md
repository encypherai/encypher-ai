# Relationship to C2PA Standards

EncypherAI takes inspiration from the [Coalition for Content Provenance and Authenticity (C2PA)](https://c2pa.org/) standard for structured content authenticity manifests, specifically adapted for plain text environments where traditional file-based embedding methods aren't applicable.

## What is C2PA?

The Coalition for Content Provenance and Authenticity (C2PA) is a Joint Development Foundation project that brings together stakeholders across various industries to develop technical standards for certifying the source and history (provenance) of media content. C2PA's goal is to address the prevalence of misleading information online by enabling content provenance and authenticity at scale.

C2PA defines specifications for embedding cryptographically verifiable metadata within media files (images, videos, audio, and documents), creating a tamper-evident record of the content's origin and edit history.

## EncypherAI's Complementary Approach

EncypherAI positions itself as a **complementary extension** to C2PA, specifically addressing the plain-text niche that C2PA's file-based approach doesn't currently cover.

### Key Alignments with C2PA

- **Structured Provenance Manifests**: EncypherAI's `manifest` format is directly inspired by C2PA's structured approach to recording content provenance information.
- **Cryptographic Integrity**: Like C2PA, EncypherAI uses digital signatures (Ed25519) to ensure tamper-evidence and content authenticity.
- **Claim Generators and Assertions**: EncypherAI adopts similar concepts to C2PA's assertions about content creation and modification.
- **Shared Mission**: Both EncypherAI and C2PA share the goal of improving content transparency, attribution, and trust.

### Key Differences from C2PA

- **Embedding Mechanism**: While C2PA embeds manifests within file structures of media formats, EncypherAI embeds metadata directly within the text content itself using Unicode variation selectors.
- **Plain Text Focus**: EncypherAI is specifically designed for text-only content (like chatbot outputs, generated articles, etc.) where standard C2PA file embedding isn't possible.
- **Simplified Structure**: EncypherAI's manifest structure is tailored for the specific context of AI-generated text, focusing on the most relevant information.

## Technical Implementation

EncypherAI's manifest format includes fields that parallel C2PA concepts:

```python
class ManifestPayload(TypedDict):
    """
    Structure for the 'manifest' metadata format payload.

    Inspired by the Coalition for Content Provenance and Authenticity (C2PA) manifests,
    this structure provides a standardized way to embed provenance information
    directly within text content.
    """
    claim_generator: str  # Software/tool that generated the claim
    assertions: List[Dict]   # Assertions about the content (similar to C2PA assertions)
    ai_assertion: Dict      # AI-specific assertion (model ID, etc.)
    custom_claims: Dict   # Custom C2PA-like claims
    timestamp: str        # ISO 8601 UTC format string
```

When using the `manifest` format with `UnicodeMetadata.embed_metadata()`, EncypherAI creates a structured record of content provenance that conceptually aligns with C2PA's approach, while using a different technical mechanism for embedding.

## Interoperability Considerations

While EncypherAI's approach is not formally C2PA compliant (due to the fundamental difference in embedding mechanisms), we provide tools to enhance interoperability:

- **Standardized Manifest Formats**: Our manifest fields are directly aligned with C2PA terminology where appropriate.
- **Conversion Utilities**: EncypherAI includes the `encypher.interop.c2pa` module with utilities to convert between EncypherAI manifests and C2PA-like JSON structures:
  ```python
  from encypher.interop.c2pa import encypher_manifest_to_c2pa_like_dict, c2pa_like_dict_to_encypher_manifest

  # Create an EncypherAI manifest
  manifest = ManifestPayload(
      claim_generator="EncypherAI/1.1.0",
      assertions=[{"label": "c2pa.created", "when": "2025-04-13T12:00:00Z"}],
      ai_assertion={"model_id": "gpt-4o", "model_version": "1.0"},
      custom_claims={},
      timestamp="2025-04-13T12:00:00Z"
  )

  # Convert EncypherAI manifest to C2PA-like structure
  c2pa_dict = encypher_manifest_to_c2pa_like_dict(manifest)

  # Convert C2PA-like structure to EncypherAI manifest
  encypher_manifest = c2pa_like_dict_to_encypher_manifest(c2pa_dict)
  ```
- **Schema Documentation**: The interoperability module includes a `get_c2pa_manifest_schema()` function that returns a JSON Schema describing the C2PA-like structure used.

### CBOR-encoded Assertion Data

For closer alignment with C2PA practices, especially when dealing with assertion data that might be binary or complex, EncypherAI now supports CBOR (Concise Binary Object Representation) encoding for the `data` field within assertions.

When converting a C2PA-like dictionary to an EncypherAI manifest, you can opt to serialize the assertion `data` into CBOR and then Base64-encode it. This is achieved by passing the `encode_assertion_data_as_cbor=True` argument to the `c2pa_like_dict_to_encypher_manifest` function. The resulting EncypherAI assertion will then include a `data_encoding: "cbor_base64"` field to indicate how the `data` (which will be a Base64 string) should be interpreted.

```python
# Example: Converting with CBOR-encoded assertion data
encypher_ai_payload_cbor = c2pa_like_dict_to_encypher_manifest(
    original_c2pa_like_manifest,
    encode_assertion_data_as_cbor=True
)
# The 'data' field in assertions within encypher_ai_payload_cbor will be a Base64 string
# and will have a 'data_encoding': 'cbor_base64' field.
```

The `encypher_manifest_to_c2pa_like_dict` function automatically detects the `data_encoding` field. If it's set to `"cbor_base64"`, it will decode the Base64 string and deserialize the CBOR data back into its original Python dictionary form.

This feature is particularly useful when the assertion `data` itself is intended to represent a C2PA assertion that might contain binary content or requires a more compact representation than JSON.

### Full CBOR Manifest Embedding

For maximum C2PA compatibility and efficiency, EncypherAI v2.3.0 introduces the `cbor_manifest` format. This goes beyond just encoding individual assertion data fields and allows you to embed a complete, C2PA-compliant manifest directly into text, with the entire manifest serialized using CBOR.

#### How It Works

When you use `metadata_format="cbor_manifest"` with `UnicodeMetadata.embed_metadata()`, EncypherAI performs the following steps:

1. **Conversion**: The manifest is converted to EncypherAI's internal format using `c2pa_like_dict_to_encypher_manifest` with `use_nested_data=True` to preserve the original nested structure of assertion data.
2. **CBOR Serialization**: The entire manifest dictionary is serialized into a compact byte string using CBOR.
3. **Signing & Encoding**: The CBOR byte string is digitally signed, and the resulting signature and payload are Base64-encoded.
4. **Embedding**: The final encoded string is embedded invisibly into the text using Unicode variation selectors.

This approach ensures that the complete, unaltered C2PA manifest can be recovered during extraction, providing a robust, end-to-end provenance solution for plain text.

#### Example: Full CBOR Manifest Embedding

```python
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest, encypher_manifest_to_c2pa_like_dict
import json

# Generate keys for signing and verification
private_key, public_key = generate_ed25519_key_pair()
signer_id = "c2pa-demo-key-001"

# Define a C2PA-like manifest with nested JSON-LD data
c2pa_manifest = {
    "claim_generator": "EncypherAI/2.3.0",
    "timestamp": "2025-06-15T12:00:00Z",
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org",
                "@type": "CreativeWork",
                "author": {
                    "@type": "Person",
                    "name": "Jane Doe"
                },
                "dateCreated": "2025-06-15"
            }
        }
    ]
}

# Convert the C2PA-like manifest for CBOR embedding
# use_nested_data=True preserves the JSON-LD structure inside assertions
encypher_manifest = c2pa_like_dict_to_encypher_manifest(
    c2pa_manifest, use_nested_data=True
)

# Embed the manifest using the 'cbor_manifest' format
original_text = "This text contains a full C2PA manifest serialized with CBOR."
embedded_text = UnicodeMetadata.embed_metadata(
    text=original_text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="cbor_manifest",  # Use the CBOR manifest format
    claim_generator=encypher_manifest.get("claim_generator"),
    actions=encypher_manifest.get("actions"),
    timestamp=encypher_manifest.get("timestamp")
)

# Extract and verify the CBOR manifest
is_verified, extracted_signer_id, extracted_manifest = UnicodeMetadata.verify_and_extract_metadata(
    text=embedded_text,
    public_key_provider=lambda kid: public_key if kid == signer_id else None
)

# Convert the extracted manifest back to a C2PA-like dictionary
if is_verified and extracted_manifest:
    reverted_c2pa_manifest = encypher_manifest_to_c2pa_like_dict(extracted_manifest)

    # The round-trip should be lossless
    assert reverted_c2pa_manifest == c2pa_manifest
    print("Round-trip successful: Original and extracted manifests match.")
```

#### Key Benefits of Full CBOR Manifest Embedding

- **Compact Representation**: CBOR is more space-efficient than JSON, allowing for more complex manifests to be embedded in text.
- **Binary Data Support**: CBOR natively supports binary data types, which can be important for certain C2PA assertions.
- **Structural Fidelity**: The entire manifest structure is preserved exactly as it was created, ensuring no information is lost during embedding and extraction.
- **C2PA Alignment**: This approach brings EncypherAI's text embedding capabilities closer to the C2PA standard's data representation practices.

#### When to Use Each Approach

- **Standard JSON Manifest** (`metadata_format="manifest"`): Best for simple provenance information and maximum compatibility with older versions.
- **CBOR-encoded Assertion Data** (`encode_assertion_data_as_cbor=True`): Good middle ground when you need efficient encoding of complex assertion data but want to keep the overall manifest structure in JSON.
- **Full CBOR Manifest** (`metadata_format="cbor_manifest"`): Ideal for maximum C2PA compatibility and when embedding complex manifests with nested structures that must be preserved exactly.

### Example: Embedding a C2PA-style Manifest in Text (with JSON and CBOR options)

The following example demonstrates the complete round-trip process of taking a C2PA-style manifest, embedding it into text using EncypherAI's `UnicodeMetadata`, extracting it, and converting it back to verify structural fidelity.

```python
import json
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import (
    c2pa_like_dict_to_encypher_manifest,
    encypher_manifest_to_c2pa_like_dict,
)

def run_c2pa_text_embedding_demo():
    print("--- EncypherAI C2PA-style Text Embedding Demo ---")

    # 1. Define an original C2PA-like manifest
    # This structure is inspired by C2PA, particularly for assertions like 'stds.schema-org.CreativeWork'.
    original_c2pa_like_manifest = {
        "claim_generator": "DemoApp/1.0.0",
        "timestamp": "2025-07-04T10:00:00Z", # Top-level timestamp for the C2PA-like manifest
        "assertions": [
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "http://schema.org/",
                    "@type": "CreativeWork",
                    "author": {
                        "@type": "Person",
                        "name": "Jane Doe"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Content Creators Inc."
                    },
                    "copyrightHolder": {
                        "name": "Content Creators Inc."
                    },
                    "copyrightYear": 2025,
                    "copyrightNotice": "© 2025 Content Creators Inc. All Rights Reserved."
                }
            }
        ]
    }
    print("\n1. Original C2PA-like Manifest:")
    print(json.dumps(original_c2pa_like_manifest, indent=2))

    # 2. Convert the C2PA-like manifest to EncypherAI's internal ManifestPayload format (JSON default)
    # The 'timestamp' from the C2PA-like manifest is used to populate the 'when' field in EncypherAI assertions.
    encypher_ai_payload_to_embed_json = c2pa_like_dict_to_encypher_manifest(original_c2pa_like_manifest)
    print("\n2. Converted EncypherAI ManifestPayload (for embedding - JSON default):")
    print(json.dumps(encypher_ai_payload_to_embed_json, indent=2))

    # 2b. Convert with CBOR-encoded assertion data
    encypher_ai_payload_to_embed_cbor = c2pa_like_dict_to_encypher_manifest(
        original_c2pa_like_manifest,
        encode_assertion_data_as_cbor=True
    )
    print("\n2b. Converted EncypherAI ManifestPayload (for embedding - CBOR assertion data):")
    # Note: The 'data' field in assertions will be a Base64 string, and 'data_encoding' will be 'cbor_base64'
    print(json.dumps(encypher_ai_payload_to_embed_cbor, indent=2))

    # For this demo, we'll proceed with the JSON-encoded version (encypher_ai_payload_to_embed_json)
    # for simplicity in showing the subsequent embedding steps.
    # The CBOR version (encypher_ai_payload_to_embed_cbor) would be embedded and extracted identically;
    # the conversion and embedding/extraction functions handle the encoding/decoding transparently.
    encypher_ai_payload_to_embed = encypher_ai_payload_to_embed_json
    print("\n--- Proceeding with JSON version for embedding demo --- ")
    # print(json.dumps(encypher_ai_payload_to_embed, indent=2)) # Already printed above

    # Generate Ed25519 keys for signing and verification
    private_key, public_key = generate_ed25519_key_pair()
    key_id = "c2pa-demo-key-doc-001"

    sample_article_text = ("This is a sample article. It discusses important topics and presents factual information. "
                           "The integrity of this text can be verified using the embedded metadata.")

    # 3. Embed the EncypherAI ManifestPayload into the sample text
    text_with_embedded_metadata = UnicodeMetadata.embed_metadata(
        text=sample_article_text,
        private_key=private_key,
        signer_id=key_id,
        metadata_format="manifest",
        claim_generator=encypher_ai_payload_to_embed.get("claim_generator"),
        actions=encypher_ai_payload_to_embed.get("assertions"),
        ai_info=encypher_ai_payload_to_embed.get("ai_assertion", {}),
        custom_claims=encypher_ai_payload_to_embed.get("custom_claims", {}),
        timestamp=encypher_ai_payload_to_embed.get("timestamp") # This is the manifest's own timestamp
    )
    print("\n3. Text with Embedded Metadata (excerpt):", text_with_embedded_metadata[:70] + "...")

    # 4. Extract and verify the metadata from the text
    def public_key_resolver(kid: str):
        if kid == key_id:
            return public_key
        raise ValueError(f"Unknown key_id: {kid}")

    is_verified, extracted_signer_id, extracted_payload_outer = UnicodeMetadata.verify_and_extract_metadata(
        text=text_with_embedded_metadata,
        public_key_provider=public_key_resolver,
        return_payload_on_failure=True
    )

    print("\n4. Extracted EncypherAI ManifestPayload (outer structure):")
    # The actual manifest is nested under the 'manifest' key
    print(json.dumps(extracted_payload_outer, indent=2))

    assert is_verified, "Signature verification failed!"
    assert extracted_signer_id == key_id, "Signer ID mismatch!"

    # 5. Verify the extracted payload details
    print("\n5. Verification Status:")
    if is_verified:
        print(f"   SUCCESS: Signature verified for signer_id: {extracted_signer_id}")
    else:
        print("   FAILURE: Signature verification failed.")

    # 6. Convert the extracted EncypherAI ManifestPayload back to a C2PA-like dictionary
    if extracted_payload_outer and 'manifest' in extracted_payload_outer:
        inner_manifest = extracted_payload_outer['manifest']
        manifest_for_conversion = {
            "claim_generator": inner_manifest.get("claim_generator"),
            "assertions": inner_manifest.get("actions"), # Map 'actions' back to 'assertions'
            "ai_assertion": inner_manifest.get("ai_assertion", {}),
            "custom_claims": inner_manifest.get("custom_claims", {}),
            "timestamp": inner_manifest.get("timestamp", extracted_payload_outer.get("timestamp"))
        }
        extracted_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(manifest_for_conversion)
        print("\n6. Extracted Payload converted back to C2PA-like Dictionary:")
        print(json.dumps(extracted_c2pa_like_dict, indent=2))

        # Verify round-trip fidelity (conceptual check, actual comparison can be more rigorous)
        assert extracted_c2pa_like_dict["assertions"][0]["data"]["author"]["name"] == \
               original_c2pa_like_manifest["assertions"][0]["data"]["author"]["name"]
        print("\n   Round-trip check: Author name matches original.")
    else:
        print("Could not perform final conversion: extracted payload or inner manifest missing.")

    print("\n--- End of Demo ---")

if __name__ == '__main__':
    run_c2pa_text_embedding_demo()
```

This example illustrates how a C2PA-style manifest, often used for rich media, can be adapted and embedded within plain text using EncypherAI. The process involves converting the C2PA-like structure to EncypherAI's native manifest format, embedding this into text, and then extracting and converting it back. This demonstrates that the core provenance information, structured in a C2PA-aligned manner, can be preserved and verified even in text-only environments.

- **Potential Sidecar Files**: Future exploration of standardized sidecar files that could complement the in-text embedding.

## Use Cases

EncypherAI's C2PA-inspired approach is particularly valuable for:

- **AI-Generated Text**: Embedding provenance information in chatbot outputs, generated articles, or other text-only AI content.
- **Plain Text Workflows**: Adding provenance to content in formats or environments where file-based C2PA embedding isn't feasible.
- **Cross-Media Workflows**: Complementing C2PA-embedded rich media with provenance-enabled plain text.

## Future Directions

As the content provenance ecosystem evolves, EncypherAI will continue to monitor C2PA developments and explore deeper alignment and potential standardization for text provenance approaches.

For more information about C2PA, visit the [official C2PA website](https://c2pa.org/).
