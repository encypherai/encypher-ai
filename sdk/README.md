# Encypher SDK Generation

Auto-generate SDKs for Python, TypeScript, Go, and Rust from the Enterprise API's OpenAPI specification.

## Quick Start

```bash
# Generate fresh OpenAPI spec from the API
uv run python sdk/generate_openapi.py

# Generate specific SDK
uv run python sdk/generate_sdk.py python
uv run python sdk/generate_sdk.py typescript
uv run python sdk/generate_sdk.py go
uv run python sdk/generate_sdk.py rust

# Generate all SDKs
uv run python sdk/generate_sdk.py all

# With verbose output
uv run python sdk/generate_sdk.py all --verbose
```

## Directory Structure

```
sdk/
├── openapi.json          # Generated OpenAPI 3.1 spec (source of truth)
├── generate_openapi.py   # Script to regenerate spec from API
├── generate_sdk.py       # SDK generation script with rich logging
├── python/               # Generated Python SDK
│   ├── encypher/
│   │   ├── api/          # 22 API modules
│   │   ├── models/       # 117 model classes
│   │   └── client.py     # High-level wrapper
│   └── pyproject.toml
├── typescript/           # Generated TypeScript SDK
│   ├── src/
│   │   ├── apis/
│   │   ├── models/
│   │   └── client.ts     # High-level wrapper
│   └── package.json
├── go/                   # Generated Go SDK
│   ├── *.go              # API and model files
│   ├── client.go         # High-level wrapper
│   └── go.mod
└── rust/                 # Generated Rust SDK
    ├── src/
    │   ├── apis/
    │   ├── models/
    │   └── client.rs     # High-level wrapper
    └── Cargo.toml
```

## OpenAPI Spec

The `openapi.json` file is auto-generated from the Enterprise API's FastAPI routes:

- **68 endpoints** across 21 tags
- **113 schemas** for request/response models
- Bearer token authentication

### Regenerating the Spec

```bash
uv run python sdk/generate_openapi.py
```

## SDK Usage Examples

### Python

```python
from encypher.client import EncypherClient

client = EncypherClient(api_key="ency_...")
result = client.sign("Hello, world!")
print(result.signed_text)
```

### TypeScript

```typescript
import { EncypherClient } from '@encypher/sdk';

const client = new EncypherClient({ apiKey: 'ency_...' });
const result = await client.sign({ text: 'Hello, world!' });
console.log(result.signedText);
```

### Go

```go
import "github.com/encypherai/sdk-go"

client := encypher.NewClient("ency_...")
result, err := client.Sign(ctx, "Hello, world!")
fmt.Println(result.SignedText)
```

### Rust

```rust
use encypher::Client;

let client = Client::new("ency_...");
let result = client.sign("Hello, world!").await?;
println!("{}", result.signed_text);
```

## Prerequisites

The generator uses `openapi-generator-cli` via npx (auto-downloads on first use):

```bash
# Or install globally
npm install -g @openapitools/openapi-generator-cli
```

## Versioning

SDK versions follow the API version in `openapi.json`:

| API Version | Python | TypeScript/Go/Rust |
|-------------|--------|-------------------|
| `1.0.0-preview` | `1.0.0a1` | `1.0.0-alpha.1` |
| `1.0.0-beta` | `1.0.0b1` | `1.0.0-beta.1` |
| `1.0.0` | `1.0.0` | `1.0.0` |

## Publishing (Future)

### Python (PyPI)

```bash
cd sdk/python
uv build
uv publish
```

### TypeScript (npm)

```bash
cd sdk/typescript
npm publish --access public
```

### Go (GitHub)

```bash
cd sdk/go
git tag v1.0.0-alpha.1
git push origin v1.0.0-alpha.1
```

### Rust (crates.io)

```bash
cd sdk/rust
cargo publish
```
