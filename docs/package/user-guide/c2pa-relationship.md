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
- **Potential Sidecar Files**: Future exploration of standardized sidecar files that could complement the in-text embedding.

## Use Cases

EncypherAI's C2PA-inspired approach is particularly valuable for:

- **AI-Generated Text**: Embedding provenance information in chatbot outputs, generated articles, or other text-only AI content.
- **Plain Text Workflows**: Adding provenance to content in formats or environments where file-based C2PA embedding isn't feasible.
- **Cross-Media Workflows**: Complementing C2PA-embedded rich media with provenance-enabled plain text.

## Future Directions

As the content provenance ecosystem evolves, EncypherAI will continue to monitor C2PA developments and explore deeper alignment and potential standardization for text provenance approaches.

For more information about C2PA, visit the [official C2PA website](https://c2pa.org/).
