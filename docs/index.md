# Encypher Documentation

<div align="center">
  <img src="assets/horizontal-logo.png" alt="Encypher Logo" width="600"/>
  <h2>Invisible Metadata for AI-Generated Text</h2>
</div>

## Welcome to Encypher

Encypher is an open-source Python package that enables invisible metadata embedding in AI-generated text using zero-width characters.

This documentation provides comprehensive information about the Encypher package, including installation instructions, usage examples, API reference, and integration guides.

## Key Features

| Feature | Description |
|---------|-------------|
| **Invisible Embedding** | Add metadata without changing visible content. |
| **Digital Signature Verification** | Ensure data integrity and detect tampering with Ed25519 signatures. |
| **C2PA-Inspired Manifests** | Embed structured, verifiable manifests for text provenance. |
| **Streaming Support** | Compatible with chunk-by-chunk streaming from LLMs. |
| **Modular Architecture** | Clean separation of key management, payload handling, and signing. |
| **Extensible API** | Easily integrate with any LLM provider. |


## Demo Video

<div align="center">
  <a href="https://www.youtube.com/watch?v=_MNP0nHc77k">
    <img src="https://img.youtube.com/vi/_MNP0nHc77k/0.jpg" alt="Encypher Demo Video" width="600"/>
  </a>
  <p>Watch our demo video to see Encypher in action</p>
</div>

## Getting Started

- [Installation](package/getting-started/installation.md)
- [Quick Start Guide](package/getting-started/quickstart.md)

## User Guide

- [Basic Usage](package/user-guide/basic-usage.md)
- [Metadata Encoding](package/user-guide/metadata-encoding.md)
- [Extraction and Verification](package/user-guide/extraction-verification.md)
- [Tamper Detection](package/user-guide/tamper-detection.md)
- [Streaming Support](package/user-guide/streaming.md)
- [C2PA Relationship](package/user-guide/c2pa-relationship.md)
- [Migration Guide](package/user-guide/migration-guide.md)

## Examples

- [Jupyter Notebook](package/examples/jupyter.md)
- [YouTube Demo](package/examples/youtube-demo.md)
- [FastAPI Integration](package/examples/fastapi.md)
- [Streamlit Demo](package/examples/streamlit.md)

## Enterprise SDK

- [Enterprise SDK Overview](package/sdk/index.md)
- Enterprise API reference: `enterprise_api/docs/API.md`
- Source code: `enterprise_sdk/` within the commercial repository

## API Reference

- [`UnicodeMetadata`](package/api-reference/unicode-metadata.md): Core class for embedding and verification.
- [`c2pa_interop`](package/api-reference/c2pa_interop.md): Utilities for C2PA compatibility.
- [Deprecated Classes](package/api-reference/metadata-encoder.md): Info on legacy classes.

## Contributing

We welcome contributions to Encypher! Check out our [contribution guidelines](package/contributing.md) to get started.

## License

Encypher is provided under a dual licensing model designed to support both open-source community use via an [AGPL-3.0 License](package/licensing.md) and commercial enterprise adoption via commercial licenses.

## GitHub Repository

Visit our [GitHub repository](https://github.com/encypherai/encypher-ai) to access the source code, report issues, or contribute to the project.
