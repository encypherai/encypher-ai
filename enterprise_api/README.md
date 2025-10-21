# Encypher Enterprise API

> Production-ready API for C2PA-compliant content signing and verification

[![Status](https://img.shields.io/badge/status-preview-yellow)](https://github.com/encypherai/encypherai-commercial)
[![License](https://img.shields.io/badge/license-proprietary-red)](../LICENSE)

## Overview

The Encypher Enterprise API provides a complete infrastructure for organizations (publishers, legal/finance firms, AI labs, enterprises) to sign content with C2PA manifests, verify signatures, and track sentence-level provenance.

**Key Features:**
- ✅ **C2PA 2.2 Compliance**: Industry-standard signatures using Ed25519 + C2PA manifests
- ✅ **Sentence-Level Tracking**: Granular provenance for individual sentences
- ✅ **SSL.com Integration**: Automated certificate provisioning from trusted CA
- ✅ **Court-Admissible Evidence**: Tamper-proof signatures for legal use
- ✅ **Fast Verification**: <100ms response times for verification
- ✅ **Independent Verification**: Public endpoints for anyone to verify content

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
- [ ] Add webhook support
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
