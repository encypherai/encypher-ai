# Changelog

This document provides a chronological list of notable changes for each version of EncypherAI.

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
