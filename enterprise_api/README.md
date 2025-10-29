# Encypher Enterprise API

> Production-ready API for C2PA-compliant content signing and verification

[![Status](https://img.shields.io/badge/status-preview-yellow)](https://github.com/encypherai/encypherai-commercial)
[![License](https://img.shields.io/badge/license-proprietary-red)](../LICENSE)

## Overview

The Encypher Enterprise API provides a complete infrastructure for organizations (publishers, legal/finance firms, AI labs, enterprises) to sign content with C2PA manifests, verify signatures, and track sentence-level provenance.

**Key Features:**
- **C2PA 2.2 compliance** via Ed25519 signatures and manifest stores
- **Sentence-level tracking** for paragraph and sentence provenance
- **SSL.com integration** with automated certificate lifecycle management
- **Court-admissible evidence** through tamper-evident manifests
- **Fast verification** (<100 ms typical) with public verification endpoints
- **Independent verification** for auditors, regulators, and readers


## C2PA Text Manifest Compliance

Our basic text signing flow implements the `C2PATextManifestWrapper` defined in [docs/c2pa/Manifests_Text.adoc](../docs/c2pa/Manifests_Text.adoc). In practice this means:

- We wrap each manifest store with the literal `C2PATXT\0` header and encode bytes strictly as Unicode variation selectors.
- A single zero-width no-break space (U+FEFF) prefixes one contiguous wrapper that is appended to the end of the visible text.
- Hashes comply with the `c2pa.hash.data` assertion: text is NFC-normalised, wrapper bytes are excluded, and byte offsets are recorded in the manifest.
- Verification rejects malformed or duplicate wrappers, returning the `manifest.text.corruptedWrapper` and `manifest.text.multipleWrappers` statuses from the spec.

This keeps the “basic” tier interoperable with any validator that implements the C2PA unstructured text guidance.

## Architecture

```
┌─────────────────────────────────────────┐
│ FastAPI REST API                        │
│ (api.encypherai.com via Railway)       │
│ - POST /api/v1/sign                    │
│ - POST /api/v1/verify                  │
│ - POST /api/v1/lookup                  │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ encypher-ai Core Library (v2.9.0-beta) │
│ - UnicodeMetadata.embed_metadata()     │
│ - UnicodeMetadata.verify_metadata()    │
│ - Full C2PA manifest generation        │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ PostgreSQL (Railway)                    │
│ - organizations, documents, sentences   │
└─────────────────────────────────────────┘
```

## Quick Start

### Option A: Integrate with the Python SDK

If you need to call the Enterprise API from Python, start with the SDK published in this repository.

```bash
pip install encypher-enterprise
```

Then configure your API key and make your first signing request:

```python
import os
from encypher_enterprise import EncypherClient

os.environ["ENCYPHER_API_KEY"] = "encypher_live_xxx"

client = EncypherClient(
    api_key=os.environ["ENCYPHER_API_KEY"],
    base_url="https://api.encypherai.com",
)

result = client.sign(
    text="Breaking news: Scientists confirm a new exoplanet.",
    title="Exoplanet discovery",
)

print(result.document_id)
print(result.verification_url)
```

More SDK examples, streaming helpers, and integration adapters live in `enterprise_sdk/README.md`. The SDK roadmap is tracked in `enterprise_sdk/SDK_WBS.md`.

### Prerequisites

- Python 3.9+
- PostgreSQL 15+
- UV (recommended) or pip
- Access to preview `encypher-ai` package with C2PA support

### Installation

1. **Clone the repository:**
   ```bash
   cd encypherai-commercial/enterprise_api
   ```

2. **Install dependencies:**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Generate encryption keys:**
   ```bash
   # Generate KEY_ENCRYPTION_KEY (32 bytes)
   openssl rand -hex 32

   # Generate ENCRYPTION_NONCE (12 bytes)
   openssl rand -hex 12
   ```

5. **Initialize database:**
   ```bash
   # Set DATABASE_URL in .env first
   python scripts/init_db.py
   ```

6. **Run the API:**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## Development

### Project Structure

```
enterprise_api/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connection
│   ├── dependencies.py         # Auth & middleware
│   ├── routers/
│   │   ├── signing.py         # POST /api/v1/sign
│   │   ├── verification.py    # POST /api/v1/verify
│   │   ├── lookup.py          # POST /api/v1/lookup
│   │   ├── onboarding.py      # Certificate management
│   │   └── dashboard.py       # Usage statistics
│   ├── models/
│   │   ├── request_models.py  # Pydantic requests
│   │   └── response_models.py # Pydantic responses
│   └── utils/
│       ├── crypto_utils.py    # Key management
│       ├── sentence_parser.py # Sentence parsing
│       └── ssl_com_client.py  # SSL.com API client
├── scripts/
│   ├── init_db.py             # Database initialization
│   └── init_db.sql            # Database schema
├── tests/
│   ├── integration/           # Integration tests
│   └── unit/                  # Unit tests
└── docs/
    ├── API.md                 # API documentation
    └── QUICKSTART.md          # Quickstart guide
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/integration/test_signing_flow.py
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

## Deployment

### Railway Deployment

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create Railway project:**
   ```bash
   railway init
   railway add postgresql
   ```

3. **Set environment variables:**
   ```bash
   railway variables set KEY_ENCRYPTION_KEY=<your-key>
   railway variables set ENCRYPTION_NONCE=<your-nonce>
   railway variables set SSL_COM_API_KEY=<your-ssl-com-key>
   railway variables set ENVIRONMENT=preview
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Check status:**
   ```bash
   railway status
   railway logs
   ```

### Custom Domain Setup

Configure custom domains in Railway dashboard:
- `api.encypherai.com` → Main API
- `verify.encypherai.com` → Verification UI (future)
- `dashboard.encypherai.com` → Customer dashboard (future)

## API Documentation

See [docs/API.md](./docs/API.md) for complete API reference.

**Quick Example:**

```bash
# Sign content
curl -X POST https://api.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your content here.",
    "document_title": "Document Title"
  }'

# Verify content
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "<signed_text>"}'
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Yes | - |
| `KEY_ENCRYPTION_KEY` | 32-byte hex key for encrypting private keys | Yes | - |
| `ENCRYPTION_NONCE` | 12-byte hex nonce for encryption | Yes | - |
| `SSL_COM_API_KEY` | SSL.com API key | Yes | - |
| `SSL_COM_API_URL` | SSL.com API endpoint | No | `https://api.ssl.com/v1` |
| `API_BASE_URL` | Public API base URL | No | `https://api.encypherai.com` |
| `ENVIRONMENT` | Environment (development/preview/production) | No | `development` |

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ with asyncpg
- **Cryptography**: Ed25519, AES-GCM
- **C2PA**: encypher-ai v2.9.0-beta (preview)
- **Deployment**: Railway
- **Certificate CA**: SSL.com

## Roadmap

### Current (Preview Phase)
- [x] Core API implementation
- [x] C2PA signing/verification
- [x] Sentence-level tracking
- [x] SSL.com integration
- [ ] Integration tests
- [ ] Load testing

### Production Launch (After C2PA Spec Publication)
- [ ] Publish encypher-ai v2.9.0 to PyPI
- [ ] Switch to production SSL.com API
- [x] Webhook management APIs (event delivery rolling out Q4 2025)
- [ ] Public verification UI
- [ ] Customer dashboard

### Future Enhancements
- [ ] Batch signing API
- [ ] Advanced analytics
- [ ] Compliance reports
- [ ] Multi-region deployment

## Support

- **Documentation**: https://docs.encypherai.com
- **Email**: support@encypherai.com
- **Issues**: GitHub Issues (internal)

## License

Proprietary - EncypherAI Commercial License

Copyright (c) 2025 EncypherAI. All rights reserved.
