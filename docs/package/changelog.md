# Changelog

This document provides a chronological list of notable changes for each version of EncypherAI.

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
- Interoperability module (`encypher.interop.c2pa`) for conversion between EncypherAI and C2PA-like structures
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
- Initial stable release of EncypherAI
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
