# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-01-26

### Changed
- Python: wrapper exclusion offsets are now returned as NFC UTF-8 byte offsets and clean text exclusion uses byte offsets.

### Tests
- Python: added regression coverage for NFC UTF-8 byte offset semantics.

## [1.0.0-preview.1] - 2025-12-05

### Changed
- Version bumped to preview for C2PA working group review
- Updated installation instructions for GitHub-based preview installation
- Added preview status badge to README

### Notes
- API is stable and ready for review
- Not yet published to package registries (PyPI, npm, crates.io)
- Install directly from GitHub during preview period

---

## [1.0.0] - 2025-11-25 (Unreleased)

### Added

- **Core Embedding/Extraction**: Full implementation of C2PA Text Manifest Wrapper specification
  - `embed_manifest()` - Embed C2PA JUMBF manifests into UTF-8 text
  - `extract_manifest()` - Extract manifests from watermarked text
  - Unicode Variation Selector encoding (U+FE00..U+FE0F, U+E0100..U+E01EF)
  - NFC normalization for consistent text handling

- **Structural Validation**: Pre-embedding validation to catch issues early
  - `validate_manifest()` - Validate JUMBF structure before embedding
  - `validate_jumbf_structure()` - Detailed JUMBF box validation with strict mode
  - `validate_wrapper_bytes()` - Validate pre-encoded wrapper bytes
  - C2PA-compliant validation codes (e.g., `manifest.text.corruptedWrapper`)

- **Multi-Language Support**:
  - Python (PyPI: `c2pa-text`)
  - TypeScript/JavaScript (npm: `c2pa-text`)
  - Rust (crates.io: `c2pa-text`)
  - Go (`github.com/encypherai/c2pa-text/go`)

- **Documentation**:
  - Comprehensive README with usage examples for all languages
  - Validation API documentation
  - MIT License

### Technical Details

- Implements `C2PATextManifestWrapper` per `Manifests_Text.adoc` specification
- Magic bytes: `C2PATXT\0` (0x4332504154585400)
- Header structure: Big-endian `!8sBI` (magic + version + length)
- ZWNBSP prefix (U+FEFF) for wrapper detection
