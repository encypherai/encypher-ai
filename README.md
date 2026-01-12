<div align="center">
  <a href="https://encypherai.com">
    <img src="https://encypherai.com/encypher_full_nobg.png" alt="Encypher Corporation Logo" width="200">
  </a>

  # c2pa-text

  **A Reference Implementation for C2PA Text Embedding**

  [![Status](https://img.shields.io/badge/Status-Stable-brightgreen)](https://github.com/encypherai/c2pa-text)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![C2PA Compliant](https://img.shields.io/badge/C2PA-Compliant-blue)](https://c2pa.org)
  [![Python](https://img.shields.io/pypi/v/c2pa-text?color=3776AB&logo=python&logoColor=white)](https://pypi.org/project/c2pa-text/)
  [![NPM](https://img.shields.io/npm/v/c2pa-text?color=CB3837&logo=npm&logoColor=white)](https://www.npmjs.com/package/c2pa-text)
  [![Rust](https://img.shields.io/crates/v/c2pa-text?color=dea584&logo=rust&logoColor=white)](https://crates.io/crates/c2pa-text)
  [![Go](https://img.shields.io/badge/Go-Reference-00ADD8?logo=go&logoColor=white)](https://pkg.go.dev/github.com/encypherai/c2pa-text/go)
</div>


---

This library allows you to embed and extract [C2PA](https://c2pa.org) manifests in unstructured text (UTF-8) using invisible Unicode Variation Selectors. It is compliant with the `Manifests_Text.adoc` specification.

## Overview

C2PA manifests are typically embedded in binary files (JPEG, PNG, MP4). For plain text, this library implements a standard wrapper structure (`C2PATextManifestWrapper`) that encodes the binary C2PA Manifest Store (JUMBF) into invisible characters that persist through copy-paste operations.

This repository contains implementations for:
- **Python**: For backend services and data processing.
- **TypeScript**: For browser extensions, web apps, and Node.js.
- **Rust**: For high-performance CLI tools and Wasm.
- **Go**: For backend microservices.

## Specification

The wrapper structure is defined as:

```
Container Type: C2PATextManifestWrapper
Magic: "C2PATXT\0" (0x4332504154585400)
Version: 1
Encoding: Unicode Variation Selectors (U+FE00..U+FE0F, U+E0100..U+E01EF)
Placement: End of text, prefixed with ZWNBSP (U+FEFF)
```

## Maintenance & Support

This library is the official reference implementation maintained by **Encypher** (encypherai.com), authors of the C2PA Text Specification and active contributors to the C2PA standard.

While this library is free and permissively licensed (MIT), Encypher offers an **Enterprise API** for:
- Managing cryptographic keys at scale (HSM)
- Analytics and tracking for embedded content
- Automated verification and revocation
- Content production workflows

[Learn more about Encypher Enterprise](https://encypherai.com)

## Installation
```bash
# Python
pip install c2pa-text

# TypeScript
npm install c2pa-text

# Rust
cargo add c2pa-text

# Go
go get github.com/encypherai/c2pa-text/go@v1.0.3
```

## Generating Manifests

This library handles the **embedding layer** (text steganography). To generate the valid C2PA JUMBF manifest bytes (`manifest_bytes`), you have two options:

### 1. Use Encypher API (Recommended)
The [Encypher Enterprise API](https://encypherai.com) automatically handles key management, signing, and manifest generation. It returns the fully signed JUMBF bytes or the final watermarked text directly.

### 2. Use C2PA Tooling
Since standard tools (like `c2patool`) do not natively support .txt files, you cannot embed directly using the CLI.

Instead, you must use the **C2PA Rust or Python SDKs** to generate a **detached manifest** (treating the text as a generic byte stream). You can then pass the resulting binary JUMBF data to this library for embedding.

## Usage (Python)

```python
from c2pa_text import embed_manifest, extract_manifest

# 1. You have a binary C2PA manifest (JUMBF)
manifest_bytes = b"..." 

# 2. Embed it into text
text = "Hello World"
watermarked_text = embed_manifest(text, manifest_bytes)

# 3. Extract it back
extracted_bytes, clean_text = extract_manifest(watermarked_text)
```

### Validation (Python)

Validate manifest structure before embedding to catch issues early:

```python
from c2pa_text import validate_manifest, embed_manifest

# Validate before embedding
result = validate_manifest(manifest_bytes)
if result.valid:
    watermarked = embed_manifest(text, manifest_bytes)
else:
    print(result)  # Shows detailed validation issues
    # Example output:
    # Validation failed:
    #   - [manifest.jumbf.truncated] JUMBF truncated: declared size 100, actual 8
```

Available validation functions:
- `validate_manifest(bytes)` - Validate JUMBF structure before embedding
- `validate_jumbf_structure(bytes, strict=True)` - Strict C2PA compliance checks
- `validate_wrapper_bytes(bytes)` - Validate pre-encoded wrapper bytes

Validation codes follow the C2PA specification (e.g., `manifest.text.corruptedWrapper`).

## Usage (TypeScript)

```typescript
import { embedManifest, extractManifest, validateManifest } from 'c2pa-text';

// 1. You have a binary C2PA manifest (JUMBF) as a Uint8Array
const manifestBytes = new Uint8Array([/* ... */]);

// 2. Validate before embedding (optional but recommended)
const validation = validateManifest(manifestBytes);
if (!validation.valid) {
  console.error(validation.issues);
  throw new Error('Invalid manifest');
}

// 3. Embed it into text
const text = "Hello World";
const watermarkedText = embedManifest(text, manifestBytes);

// 4. Extract it back
const result = extractManifest(watermarkedText);
if (result) {
  console.log(result.manifest);   // Uint8Array
  console.log(result.cleanText);  // "Hello World"
}
```

## Usage (Rust)

```rust
use c2pa_text::{embed_manifest, extract_manifest, validate_manifest};

// 1. Binary manifest
let manifest_bytes = b"...";

// 2. Validate before embedding (optional but recommended)
let validation = validate_manifest(manifest_bytes, true, false);
if !validation.valid {
    eprintln!("{}", validation);
    return Err("Invalid manifest");
}

// 3. Embed
let text = "Hello World";
let watermarked = embed_manifest(text, manifest_bytes);

// 4. Extract
if let Ok(result) = extract_manifest(&watermarked) {
    if let Some(bytes) = result.manifest {
        println!("Extracted {} bytes", bytes.len());
    }
}
```

## Usage (Go)

```go
import "github.com/encypherai/c2pa-text/go/c2pa_text"

// 1. Binary manifest
manifestBytes := []byte("...")

// 2. Validate before embedding (optional but recommended)
validation := c2pa_text.ValidateManifest(manifestBytes, true, false)
if !validation.Valid {
    fmt.Println(validation)
    return errors.New("invalid manifest")
}

// 3. Embed
text := "Hello World"
watermarked := c2pa_text.EmbedManifest(text, manifestBytes)

// 4. Extract
extractedBytes, cleanText, _, _, err := c2pa_text.ExtractManifest(watermarked)
```

## License

MIT
