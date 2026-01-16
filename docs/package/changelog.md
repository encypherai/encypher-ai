# Changelog

This document provides a chronological list of notable changes for each version of Encypher.

## 3.0.3 (2026-01-16)

### Fixed
- Made C2PA manifest `@context` handling configurable via environment variables:
  - `ENCYPHER_C2PA_CONTEXT_URL` controls the emitted `@context` during embedding.
  - `ENCYPHER_C2PA_ACCEPTED_CONTEXTS` controls the verifier allowlist (JSON list or comma-separated string).
- Default verifier allowlist accepts both C2PA schema contexts v2.2 and v2.3 to avoid false `SIGNATURE_INVALID` failures when signing emits v2.3.
- Restored green CI by fixing `mypy` typing issues:
  - Corrected internal helper type signatures.
  - Added missing return type annotations.
  - Cleaned up unused imports caught by linters.

## 3.0.2 (2026-01-10)

### Added
- Introduced a shared `text_hashing` helper in `encypher.interop.c2pa` that performs NFC normalisation, exclusion filtering, and SHA-256 hashing so embedding and verification reuse the exact same pipeline.
- Documented the end-of-text `C2PATextManifestWrapper` flow, including the FEFF prefix, contiguous variation selector block, and wrapper exclusion handling mandated by the latest C2PA text embedding proposal.
- Implemented native COSE_Sign1 EdDSA (Ed25519) signing/verification using `cbor2` + `cryptography` (no external COSE runtime required).

### Changed
- Updated the C2PA embedding path to always append a single FEFF-prefixed wrapper containing a JUMBF manifest store encoded with the `magic | version | length | payload` layout.
- Refactored hard-binding exclusion tracking to record `{start, length}` byte ranges derived from the NFC-normalised text and to stabilise those offsets prior to signing.
- Removed `pycose` usage and replaced with a minimal COSE_Sign1 EdDSA implementation (Ed25519). Behaviour is unchanged for EdDSA-based claims; X.509 x5chain handling preserved.

### Fixed
- Ensured validators normalise text, remove wrapper exclusions, and recompute the content hash using the shared helper, eliminating discrepancies between embedding and verification.
- Accepted C2PA manifest `@context` values for both v2.2 and v2.3 during verification.

### Documentation
- Refreshed C2PA API references, tutorials, and provenance guides to explain the FEFF-prefixed wrapper workflow, normalised hashing routine, and the new helper utilities.
- Noted release plan: 3.0 will target C2PA 2.3 alignment and include the native COSE path.

### Security
- Dependency hygiene: Eliminated transitive `python-ecdsa` (GHSA-wj6h-64fc-37mp) by removing `pycose` and using a native COSE EdDSA implementation.

## 3.0.0 (2025-11-23)

### Breaking Changes
- **Dependency Optimization:** Removed `litellm` from core dependencies. If you relied on `encypher-ai` to install `litellm`, you must now install it explicitly or use `encypher-ai[dev]` for examples.
- **Standardization:** Refactored core C2PA embedding logic to rely on the new `c2pa-text` reference library.

### Added
- **Dependency:** Added `c2pa-text` as a core dependency for low-level C2PA compliance.
- **Dependency:** Added `requests` as a core dependency (required for timestamping).

### Changed
- **Developer Experience:** Replaced `black`, `flake8`, and `isort` with `ruff` for faster and more unified linting/formatting.
- **Typing:** Modernized type hints across the codebase.

## 2.8.1 (2025-01-03)

### Fixed
- Fixed critical `IndentationError` in `unicode_metadata.py` that prevented test collection and metadata extraction
- Fixed missing `custom_metadata` in manifest and cbor_manifest formats during embedding
- Fixed `custom_metadata` extraction by implementing proper payload flattening for manifest formats
- Enhanced metadata extraction robustness with improved BOM handling and variation selector filtering
- Fixed integration test collection issues with diagnostic artifacts
- Improved FILE_END metadata extraction with better trailing marker detection

### Changed
- Split integration tests into separate success and tamper detection test suites for clearer test results
- Enhanced test coverage with comprehensive FILE_END embedding scenarios (32 test cases)
- Improved error handling and logging in metadata extraction pipeline

## 2.8.0 (08-27-2025)

### Added
- **New Embedding Targets:** Added `FILE_END` and `FILE_END_ZWNBSP` to `MetadataTarget` and as string options (`"file_end"`, `"file_end_zwnbsp"`).
  - `FILE_END`: Appends the variation selectors at the end of the text content.
  - `FILE_END_ZWNBSP`: Appends a zero-width no-break space (U+FEFF) followed by the variation selectors at the end, improving robustness in pipelines that might trim trailing selectors.
  - Documentation and examples updated to reference these targets:
    - `docs/package/api-reference/unicode_metadata.md`
    - `docs/package/api-reference/streaming-metadata-encoder.md`
    - `docs/package/streaming/handlers.md`
    - `docs/package/examples/advanced-usage.md`
    - `docs/package/examples/c2pa_text_demo.md`

### Changed
- **Timestamp Optionality:** `UnicodeMetadata.embed_metadata()` now treats `timestamp` as optional across all formats (`basic`, `manifest`, `cbor_manifest`, `c2pa`).
- **C2PA Assertions:** When no timestamp is provided, C2PA action assertions (e.g., `c2pa.created`, `c2pa.watermarked`) omit the `when` field. Behavior remains unchanged when a valid timestamp is supplied.

### Fixed
- **Interop Import:** Resolved import/name collision in `encypher.interop.c2pa` by dynamically loading the sibling `c2pa.py` within `encypher/interop/c2pa/__init__.py` and re-exporting:
  - `encypher_manifest_to_c2pa_like_dict`
  - `c2pa_like_dict_to_encypher_manifest`
  - `get_c2pa_manifest_schema`

### Documentation
- Updated `README.md` to clarify that timestamps are recommended but optional and to show usage with/without a timestamp.

## 2.7.0 (07-08-2025)

### Modified
- Changed the public API so that the metadata format uses the generic value "c2pa" instead of the older "c2pa_v2_2". The version of C2PA alignment is now tracked in the README.md.
- `metadata_format` now expects: `metadata_format: Literal["basic", "manifest", "cbor_manifest", "c2pa"] = "manifest"`

## 2.6.0 (07-07-2025)

### Added
- **Metadata Redaction:** `UnicodeMetadata.embed_metadata` and `StreamingHandler` now support an `omit_keys` parameter to remove specified metadata fields before signing. The CLI exposes this via `--omit-keys`.

## 2.5.0 (07-07-2025)

### Added
- **JUMBF Embedding:** Added support for a `jumbf` metadata format which stores
  the inner payload in a compact binary JUMBF box. The decoder now automatically
  detects JSON, CBOR, or JUMBF embeddings.

## 2.4.0 (06-28-2025)

### Added
- **C2PA v2.2 Compliance:** Re-architected the core package to be the reference implementation for text-based C2PA v2.2 soft binding. This includes:
  - **Manifest Structure:** Manifests now conform to the C2PA v2.2 specification, including the official `@context`, a unique `instance_id`, and ISO 8601 formatted timestamps.
  - **Hard Binding:** Added the mandatory `c2pa.hash.data.v1` assertion, which contains a SHA-256 hash of the clean text content for integrity verification.
  - **Soft Binding:** Implemented the `c2pa.soft_binding.v1` assertion, formalizing our Unicode Variation Selector method as `encypher.unicode_variation_selector.v1` and linking it to a `c2pa.watermarked` action.
  - **Advanced Signing:** Integrated COSE (CBOR Object Signing and Encryption) for claims, with support for X.509 certificate validation and RFC 3161 Time-Stamp Authority (TSA) integration.
- **Conditional Hard Binding Control:**
  - Introduced `add_hard_binding: bool` to `UnicodeMetadata.embed_metadata` to optionally disable hard binding, which is now the default for streaming.
  - Added `require_hard_binding: bool` to `UnicodeMetadata.verify_metadata` to allow verification of streamed content where hard binding is intentionally omitted.
- **New Internal APIs:** Added `_embed_c2pa_compliant` and `_verify_c2pa_compliant` methods to encapsulate C2PA-specific logic, along with new `TypedDict` payload structures for all C2PA assertions.

### Changed
- **Streaming Verification:** The default behavior for streaming has been updated to disable hard binding. The `StreamingHandler` now implicitly calls `embed_metadata` with `add_hard_binding=False` to prevent false verification failures on partial content.
- **Claim Generator:** The `claim_generator` field is now dynamically populated with the current package version (e.g., `encypher-ai/2.4.0`), removing the need for manual updates in future releases.

### Fixed
- **StreamingHandler Initialization**: Fixed a bug in the `StreamingHandler` where custom claims and timestamps were not being correctly passed to the embedding function, causing errors during C2PA manifest creation.
- **StreamingHandler Metadata Embedding**: Fixed a critical bug in the `StreamingHandler` where user-supplied metadata fields (especially `custom_metadata`) were not being correctly preserved in the embedded payload, causing metadata round-trip verification failures in integration tests.
- **Gemini Integration Test:** Fully repaired the Gemini integration test to correctly verify both non-streaming (with hard binding) and streaming (without hard binding) metadata, confirming the end-to-end workflow.
- **Core `UnicodeMetadata` Bugs:**
  - Restored missing `_bytes_to_variation_selectors` and `_extract_outer_payload` helper methods, resolving `AttributeError` exceptions.
  - Corrected a critical `IndentationError` in `unicode_metadata.py`.
- **Type Checking:** Fixed multiple mypy errors in the codebase:
  - Added proper null checks for COSE message payloads
  - Fixed RSA signature verification type handling
  - Added proper type annotations for timestamp requests
  - Added `types-requests` to development dependencies
  - Fixed string formatting of binary data
  - Added explicit string conversion for certificate common names and serial numbers

### Documentation
- **Comprehensive Streaming Update:** Overhauled all documentation (integration guides, README, user guides) to reflect the new `require_hard_binding=False` parameter for verifying streamed content.
- **C2PA Specification:** Added a formal algorithm specification document (`docs/c2pa_algorithm_spec.md`) detailing the technical implementation for our C2PA submission.

## 2.3.0 (06-15-2025)

### Added
- **C2PA Interoperability:**
  - Introduced a new `cbor_manifest` metadata format for embedding full C2PA-compliant manifests serialized using CBOR. This provides a more compact and standards-aligned method for storing complex claim data.
  - Added `c2pa_like_dict_to_encypher_manifest` and `encypher_manifest_to_c2pa_like_dict` conversion utilities in `encypher.interop.c2pa` to seamlessly translate between Encypher's internal manifest structure and C2PA-like dictionaries.
  - Implemented conditional logic to handle both nested assertion data (for CBOR) and flattened data structures for standard JSON manifests.
- **CBOR Support:**
  - Integrated the `cbor2` library to enable CBOR serialization and deserialization.
  - Added helper functions for encoding/decoding CBOR payloads, including Base64 wrapping for text-based embedding.
- **Documentation & Examples:**
  - Created a new example script `c2pa_text_embedding_demo.py` demonstrating the end-to-end flow of creating, embedding, and verifying a C2PA-like manifest.
  - Updated `c2pa-relationship.md` to detail the new CBOR-based manifest support and its benefits.
- **Testing:**
  - Added comprehensive integration tests for C2PA and CBOR manifest round-trips, ensuring data integrity and successful verification.

### Fixed
- **Documentation:** Corrected all streaming verification examples across integration guides (`OpenAI`, `Anthropic`, `LiteLLM`, `FastAPI`), the `README.md`, and user guides to use `require_hard_binding=False`. This ensures documentation accurately reflects that hard binding is disabled for streamed content.
- **Type Hinting:** Resolved all `mypy` static type checking errors in `encypher.core.unicode_metadata`, improving code reliability and maintainability.
- **Conversion Logic:** Corrected conversion helpers to properly retain top-level `timestamp` and `claim_generator` fields during round-trip conversions.

### Developer Changes
- Refactored `UnicodeMetadata` to support multiple manifest formats (`manifest` and `cbor_manifest`) in both embedding and extraction workflows.


## 2.2.0 (06-02-2025)

### Changed
- **Core Package Refactoring:**
  - Split `crypto_utils.py` into three specialized modules:
    - `keys.py`: Key generation, loading, and saving functions
    - `payloads.py`: Payload data structures and serialization
    - `signing.py`: Digital signature operations
  - Renamed functions for clarity:
    - `load_private_key` → `load_private_key_from_data`
    - `load_public_key` → `load_public_key_from_data`
  - Added backward compatibility layer in `crypto_utils.py` that re-exports all functions and types with deprecation warnings

### Added
- **Documentation:**
  - Added a comprehensive [Migration Guide](user-guide/migration-guide.md) to help users transition to the new module structure
  - Updated example scripts to use the new module imports

### Developer Changes
- Improved code organization following the Single Responsibility Principle
- Enhanced type hints and docstrings across all modules
- Added dedicated test file for signing functionality
- Ensured all tests pass with the new module structure

## 2.1.0 (05-23-2025)

### Changed
- **API Updates for `UnicodeMetadata` class:**
    - `embed_metadata`:
        - Now requires `signer_id` as a direct parameter (replacing `key_id` within a `metadata` dictionary).
        - Accepts other metadata components (`model_id`, `timestamp`, `organization`, `version`, `custom_metadata`, `metadata_format`) as direct parameters. The generic `metadata` dictionary parameter has been removed for clarity and type safety.
    - `verify_metadata`:
        - The `public_key_resolver` parameter has been renamed to `public_key_provider` for consistency.
        - The `public_key_provider` function now receives `signer_id` as its argument.
        - Returns a tuple: `(is_valid: bool, signer_id: Optional[str], payload: Union[BasicPayload, ManifestPayload, None])`.
    - `extract_metadata`:
        - Now consistently returns a `BasicPayload` or `ManifestPayload` object (or `None`), rather than a raw dictionary.
- **Consistent Terminology:**
    - Replaced all instances of `key_id` with `signer_id` across the API, internal logic, and documentation to better reflect its purpose.
- **`StreamingHandler` Update:**
    - The constructor (`__init__`) now accepts `signer_id` and other metadata components as direct parameters, similar to `embed_metadata`.

### Documentation
- Updated all relevant documentation files, including:
    - `quickstart.md`
    - `basic-usage.md`
    - `user-guide/extraction-verification.md`
    - `user-guide/metadata-encoding.md`
    - `api-reference/unicode-metadata.md`
- All examples revised to reflect the new API signatures, parameter changes, and the use of `signer_id`.
- Ensured all code examples are runnable and accurately demonstrate the functionalities of version 2.1.0.

## 2.0.0 (04-13-2025)

### Added
- Ed25519 digital signatures for enhanced security
- Key management utilities for generating and managing key pairs
- Public key resolver pattern for verification
- Improved API for metadata embedding and verification
- Updated documentation with digital signature examples
- C2PA-inspired manifest structure for enhanced content provenance
- Interoperability module (`encypher.interop.c2pa`) for conversion between Encypher and C2PA-like structures
- Comprehensive documentation on C2PA relationship and alignment

### Changed
- Replaced HMAC verification with Ed25519 digital signatures
- Updated `UnicodeMetadata` class to be the primary interface
- Deprecated `MetadataEncoder` and `StreamingMetadataEncoder` classes
- Improved `StreamingHandler` to use digital signatures
- Updated all examples and integration guides
- Aligned manifest field names with C2PA terminology:
  - Renamed `actions` to `assertions` in `ManifestPayload`
  - Renamed `action` to `label` in `ManifestAction`
  - Renamed `ai_info` to `ai_assertion` in `ManifestPayload`
- Updated documentation to reflect terminology changes
- Enhanced docstrings with references to C2PA concepts

### Security
- Enhanced security with asymmetric cryptography
- Separate private keys for signing and public keys for verification
- Key ID system for managing multiple keys
- Improved tamper detection capabilities

### Documentation
- Added new user guide: [Relationship to C2PA Standards](../package/user-guide/c2pa-relationship.md)
- Updated examples to use the new field names
- Added code examples for the interoperability module

## 1.0.0 (03-22-2025)

### Added
- Initial stable release of Encypher
- Core metadata encoding and decoding functionality
- HMAC verification for tamper detection
- Support for multiple embedding targets:
  - Whitespace (default)
  - Punctuation
  - First letter of words
  - Last letter of words
  - All characters
- Streaming support for handling content from LLMs
- Integration with popular LLM providers:
  - OpenAI
  - Anthropic
  - LiteLLM
- Comprehensive documentation and examples
- Interactive demos:
  - Jupyter Notebook demo
  - Streamlit web app
  - FastAPI example application
- Python client library
- JavaScript client library

### Security
- Secure HMAC verification using SHA-256
- Secret key management for verification
- Tamper detection capabilities
