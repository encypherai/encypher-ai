# EncypherAI Commercial Suite

<div align="center">

**Enterprise-grade content authentication and AI governance solutions**

[![License](https://img.shields.io/badge/license-proprietary-red)](./LICENSE)
[![C2PA 2.2](https://img.shields.io/badge/C2PA-2.2-blue)](https://c2pa.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[Overview](#-overview) • [Repository Structure](#-repository-structure) • [Getting Started](#-getting-started) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

EncypherAI is dedicated to establishing trust and verifiable provenance for AI-generated content. This repository houses the **proprietary source code** for EncypherAI's commercial software offerings, built upon our open-source `encypher-ai` core library.

**Important:** The code in this repository is proprietary, subject to EncypherAI's commercial licensing terms, and is **NOT open source**. It is intended for the internal EncypherAI development team and authorized partners.

### The EncypherAI Open-Source Core

Our public [`encypher-ai`](https://github.com/encypher-ai/encypher-ai) Python package (AGPLv3 licensed, available on PyPI) provides foundational capabilities:

- **Cryptographic Signing**: Ed25519 signatures with C2PA-compliant manifests
- **Invisible Embedding**: Unicode variation selectors for metadata embedding
- **Verification**: Tamper detection and signature validation
- **Streaming Support**: Real-time metadata processing

All commercial tools in this repository leverage the open-source core as a dependency.

---

## 📁 Repository Structure

This monorepo is organized by product tier and functionality:

### 🔧 Command-Line Tools (Free/Professional Tier)

| Directory | Tool | License Tier | Description |
|-----------|------|--------------|-------------|
| [`audit_log_cli/`](./audit_log_cli/) | **Audit Log & Report Generator** | Free/Pro | Scan text assets, validate metadata, generate compliance reports (CSV) |
| [`policy_validator_cli/`](./policy_validator_cli/) | **Policy Validation Tool** | Professional | Define and enforce custom metadata policies with JSON schemas |

### 🌐 Web Applications

| Directory | Application | Domain | Description |
|-----------|-------------|--------|-------------|
| [`apps/marketing-site/`](./apps/marketing-site/) | **Marketing Site** | `encypherai.com` | Public-facing marketing website (Next.js) |
| [`apps/dashboard/`](./apps/dashboard/) | **User Dashboard** | `dashboard.encypherai.com` | API key management, usage tracking, analytics (Next.js) |
| [`dashboard_app/`](./dashboard_app/) | **Compliance Dashboard** | Internal/Enterprise | Full-stack compliance dashboard with directory signing (FastAPI + Next.js) |

### 🚀 APIs & SDKs (Enterprise Tier)

| Directory | Product | License Tier | Description |
|-----------|---------|--------------|-------------|
| [`enterprise_api/`](./enterprise_api/) | **Enterprise API** | Enterprise | Production C2PA API with Merkle trees, source attribution, plagiarism detection |
| [`enterprise_sdk/`](./enterprise_sdk/) | **Enterprise SDK** | Enterprise | Python SDK with batch operations, CI/CD integration, framework wrappers |

### 🔧 Microservices Architecture

**Migration Status:** ✅ 100% Complete (8/8 services) | [View Progress](./docs/architecture/MICROSERVICES_PROGRESS.md)

All microservices are production-ready with full FastAPI implementations, Docker support, and comprehensive documentation.

| Directory | Service | Port | Status | Description |
|-----------|---------|------|--------|-------------|
| [`services/auth-service/`](./services/auth-service/) | **Auth Service** | 8001 | ✅ Complete | JWT authentication, OAuth (Google/GitHub), session management, token refresh |
| [`services/user-service/`](./services/user-service/) | **User Service** | 8002 | ✅ Complete | User profiles, team management, preferences, organization management |
| [`services/key-service/`](./services/key-service/) | **Key Service** | 8003 | ✅ Complete | API key generation, rotation, permissions, usage tracking, verification |
| [`services/encoding-service/`](./services/encoding-service/) | **Encoding Service** | 8004 | ✅ Complete | Document signing, metadata embedding, C2PA manifests, cryptographic operations |
| [`services/verification-service/`](./services/verification-service/) | **Verification Service** | 8005 | ✅ Complete | Signature verification, document validation, tampering detection, authenticity checks |
| [`services/analytics-service/`](./services/analytics-service/) | **Analytics Service** | 8006 | ✅ Complete | Usage statistics, performance metrics, activity tracking, reporting |
| [`services/billing-service/`](./services/billing-service/) | **Billing Service** | 8007 | ✅ Complete | Subscription management, payment processing, invoicing, billing statistics |
| [`services/notification-service/`](./services/notification-service/) | **Notification Service** | 8008 | ✅ Complete | Email notifications, SMS alerts, webhook delivery, notification history |

**Quick Start:**
```bash
# Start all services with Docker Compose
cd services
docker-compose -f docker-compose.dev.yml up

# Or run individual services
cd services/auth-service && uv run python -m app.main
cd services/key-service && uv run python -m app.main
cd services/encoding-service && uv run python -m app.main
cd services/verification-service && uv run python -m app.main
cd services/analytics-service && uv run python -m app.main
cd services/billing-service && uv run python -m app.main
cd services/notification-service && uv run python -m app.main
cd services/user-service && uv run python -m app.main
```

**Architecture:**
- 8 independent microservices
- FastAPI framework with async support
- PostgreSQL databases with SQLAlchemy ORM
- Redis caching layer
- Service-to-service authentication
- Comprehensive API documentation (OpenAPI/Swagger)
- Docker containerization
- Health check endpoints

---

## 🏛️ Architecture Decision: Microservices vs Enterprise API

### Why Two Separate Systems?

We maintain **two distinct architectures** for different use cases and customer tiers:

#### 🔧 **Microservices** (Core Platform)
**Purpose:** Foundation services for all tiers (Free, Professional, Enterprise)

**Features Included:**
- ✅ **Basic Document Signing** - Ed25519 signatures with C2PA manifests
- ✅ **Standard Verification** - Signature validation and tampering detection
- ✅ **Authentication & Authorization** - JWT, OAuth, session management
- ✅ **API Key Management** - Generation, rotation, permissions
- ✅ **User & Team Management** - Profiles, organizations, preferences
- ✅ **Usage Analytics** - Metrics, statistics, reporting
- ✅ **Billing & Subscriptions** - Payment processing, invoicing
- ✅ **Notifications** - Email, SMS, webhooks

**Best For:**
- Standard content authentication
- High-volume basic signing operations
- Multi-tenant SaaS platform
- Free and Professional tier customers

#### 🚀 **Enterprise API** (Advanced Features)
**Purpose:** Premium enterprise-only capabilities

**Features Included:**
- 🔒 **Merkle Tree Encoding** - Hierarchical content authentication
- 🔒 **Minimal Signed Embeddings** - Invisible Unicode-based content authentication with public verification
- 🔒 **Source Attribution** - Track content origins and modifications
- 🔒 **Plagiarism Detection** - Advanced content similarity analysis
- 🔒 **Batch Operations** - High-volume processing with queuing
- 🔒 **Advanced Analytics** - Deep insights and forensic analysis
- 🔒 **Custom Integrations** - Framework wrappers and CI/CD tools

**Best For:**
- Enterprise customers with complex requirements
- Content provenance tracking
- Legal and compliance use cases
- High-security applications

### 🎯 Architectural Benefits

| Benefit | Description |
|---------|-------------|
| **Clear Licensing** | Easy to enforce enterprise-only features |
| **Independent Scaling** | Scale basic and advanced features separately |
| **Security** | Enterprise algorithms protected from basic tier |
| **Simplicity** | Core services stay lean and fast |
| **Flexibility** | Deploy services independently based on needs |

### 🔄 Integration Pattern

```
┌─────────────────┐
│  Client Apps    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────────┐
│ Core │  │ Enterprise│
│ μSvcs│  │    API    │
└──────┘  └───────────┘
    │          │
    └────┬─────┘
         │
    ┌────▼────┐
    │ Storage │
    └─────────┘
```

**Customers choose based on their tier:**
- **Free/Pro:** Use microservices directly
- **Enterprise:** Use Enterprise API (which can leverage microservices for auth/billing)

---

### 🔌 Integrations

| Directory | Integration | Description |
|-----------|-------------|-------------|
| [`integrations/wordpress-assurance-plugin/`](./integrations/wordpress-assurance-plugin/) | **WordPress Plugin** | Gutenberg & Classic editor integration with Enterprise API |

### 📦 Shared Libraries & Packages

| Directory | Package | Description |
|-----------|---------|-------------|
| [`shared_commercial_libs/`](./shared_commercial_libs/) | **Commercial Shared Library** | Internal Python library with high-level APIs for all commercial tools |
| [`packages/design-system/`](./packages/design-system/) | **Design System** | Unified React/TypeScript component library for all web properties |

### 📚 Supporting Directories

| Directory | Purpose |
|-----------|---------|
| [`docs/`](./docs/) | Architecture docs, implementation plans, PRDs, API specs, C2PA reference |
| [`examples/`](./examples/) | Usage examples and sample files for commercial tools |
| [`scripts/`](./scripts/) | Development automation scripts (setup, stats, SDK generation) |
| [`PRDs/`](./PRDs/) | Product Requirements Documents for active development |

---

## 🏗️ Product Tiers & Licensing

> **Architecture Note:** Free/Pro tiers use **Microservices**, Enterprise tier adds **Enterprise API**. [See Architecture Decision](#️-architecture-decision-microservices-vs-enterprise-api)

### Free Tier
**Uses:** Core Microservices
- ✅ Audit Log CLI (basic reporting)
- ✅ C2PA-compliant signing & verification (via Encoding/Verification Services)
- ✅ Public verification pages
- ✅ 1,000 API requests/month
- ✅ Basic authentication & API keys

### Professional Tier
**Uses:** Core Microservices + Advanced Features
- ✅ All Free features
- ✅ Policy Validator CLI
- ✅ Sentence-level lookup
- ✅ Invisible signed embeddings (Unicode variation selectors)
- ✅ Custom metadata schemas
- ✅ 10,000 API requests/month
- ✅ Team management
- ✅ Usage analytics dashboard

### Enterprise Tier
**Uses:** Core Microservices + Enterprise API
- ✅ All Professional features
- ✅ **Enterprise API** (self-hosted or managed)
  - 🔒 Merkle tree encoding
  - 🔒 Invisible signed embeddings with public verification API
  - 🔒 Source attribution & plagiarism detection
  - 🔒 Batch operations with queuing
  - 🔒 Advanced forensic analysis
- ✅ Enterprise SDK (Python, CI/CD integration)
- ✅ Compliance Dashboard
- ✅ WordPress integration
- ✅ Partner integration tools (web scraping, content monitoring)
- ✅ Unlimited API requests
- ✅ SLA guarantee (99.9%)
- ✅ Dedicated support

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** with [UV](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with pnpm (for web applications)
- **Git** for version control

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/encypherai/encypherai-commercial.git
cd encypherai-commercial
```

#### 2. Set Up Python Environment

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install root dependencies
uv sync
```

#### 3. Choose Your Tool

**For CLI Tools:**
```bash
# Audit Log CLI
cd audit_log_cli
uv sync
uv run python app/main.py generate-report --help

# Policy Validator CLI
cd policy_validator_cli
uv sync
uv run python -m policy_validator_cli.app.main --help
```

**For Enterprise API:**
```bash
cd enterprise_api
cp .env.example .env
# Edit .env with your configuration
uv run uvicorn app.main:app --reload --port 9000
```

**For Web Applications:**
```bash
# Marketing Site
cd apps/marketing-site
npm install
npm run dev

# Dashboard
cd apps/dashboard
npm install
npm run dev
```

**For Compliance Dashboard:**
```bash
# Backend
cd dashboard_app/backend
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd dashboard_app/frontend
pnpm install
pnpm dev
```

---

## 📖 Documentation

### Core Documentation

- **[Enterprise API Documentation](./enterprise_api/README.md)** - Complete API reference with endpoints, authentication, examples
- **[Enterprise SDK Documentation](./enterprise_sdk/README.md)** - SDK usage, batch operations, CI/CD integration
- **[Compliance Dashboard Guide](./dashboard_app/README.md)** - Directory signing, verification workflows
- **[Design System Guide](./packages/design-system/README.md)** - Component library, brand colors, usage examples

### Microservices Documentation

- **[Auth Service](./services/auth-service/README.md)** - JWT authentication, OAuth integration, session management
- **[Key Service](./services/key-service/README.md)** - API key management, rotation, permissions
- **[Encoding Service](./services/encoding-service/README.md)** - Document signing, metadata embedding
- **[Verification Service](./services/verification-service/README.md)** - Signature verification, tampering detection
- **[Analytics Service](./services/analytics-service/README.md)** - Usage metrics, statistics, reporting
- **[Billing Service](./services/billing-service/README.md)** - Subscriptions, payments, invoicing
- **[Notification Service](./services/notification-service/README.md)** - Email, SMS, webhook notifications
- **[User Service](./services/user-service/README.md)** - User profiles, team management

### Tool-Specific Guides

- **[Audit Log CLI](./audit_log_cli/README.md)** - Scanning files, generating reports, trusted signers
- **[Policy Validator CLI](./policy_validator_cli/README.md)** - Policy schemas, validation rules, examples
- **[WordPress Plugin](./integrations/wordpress-assurance-plugin/README.md)** - Installation, configuration, Docker setup
- **[Shared Library](./shared_commercial_libs/README.md)** - High-level API, utilities, testing

### Architecture & Planning

- **[Architecture Docs](./docs/architecture/)** - System design, backend architecture, migration plans
- **[Implementation Plans](./docs/implementation_plans/)** - Phase plans, progress tracking
- **[C2PA Reference](./docs/c2pa/)** - C2PA 2.2 text manifest specification
- **[API Specs](./docs/api_specs/)** - OpenAPI/Swagger specifications

---

## 🛠️ Development Workflow

### Package Management (Python)

**ALWAYS use UV for Python package management:**

```bash
# Add a dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove package-name

# Sync environment with lockfile
uv sync

# Run commands in the environment
uv run python script.py
```

**Never edit `pyproject.toml` directly to add packages. Do not use pip commands.**

### Running Tests

```bash
# Python projects
cd <project-directory>
uv run pytest

# With coverage
uv run pytest --cov=<package-name> --cov-report=html

# JavaScript projects
cd <app-directory>
npm test
```

### Code Quality

```bash
# Python linting and formatting
uv run ruff check .
uv run black .
uv run mypy .

# JavaScript/TypeScript
npm run lint
npm run format
```

---

## 🔒 Security & Compliance

- **C2PA 2.2 Compliant**: Industry-standard content authenticity
- **Cryptographic Signatures**: Ed25519 with tamper detection
- **SSL.com Integration**: Automated certificate lifecycle management
- **Court-Admissible**: Tamper-evident manifests for legal evidence
- **SOC 2 Type II**: Enterprise security standards
- **GDPR Compliant**: Data protection and privacy

---

## 🤝 Contributing (Internal)

### Development Guidelines

1. **Branch Strategy**: Use feature branches (`feature/description`) and PR workflow
2. **Code Review**: All changes require PR approval
3. **Testing**: Maintain test coverage above 80%
4. **Documentation**: Update READMEs and docs with code changes
5. **Commit Messages**: Use conventional commits format

### Before Committing

```bash
# Run tests
uv run pytest

# Check code quality
uv run ruff check .
uv run black --check .

# Update documentation if needed
```

---

## 📊 Repository Statistics

### Microservices Migration Complete! 🎉

- **8 Production-Ready Microservices** - All services fully implemented
- **50+ API Endpoints** - Comprehensive REST APIs
- **15+ Database Models** - Complete data architecture
- **~15,000 Lines of Code** - Production-quality implementation
- **~200 Files Created** - Full service implementations
- **100% Docker Support** - All services containerized
- **Complete Documentation** - Every service documented

Run the repo stats script to see current metrics:

```bash
uv run python scripts/repo_stats.py
```

---

## 🆘 Support

- **Internal Team**: Slack #encypher-dev
- **Enterprise Customers**: enterprise@encypherai.com
- **API Issues**: api@encypherai.com
- **SDK Issues**: sdk@encypherai.com

---

## 📄 License

**Proprietary** - All rights reserved. See [LICENSE](./LICENSE) for details.

This software is confidential and proprietary to EncypherAI. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 🙏 Acknowledgments

Built with:
- [C2PA](https://c2pa.org/) - Content authenticity standards
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Railway](https://railway.app/) - Hosting platform

---

<div align="center">

**Made with ❤️ by the EncypherAI Team**

[Website](https://encypherai.com) • [Dashboard](https://dashboard.encypherai.com) • [API Docs](https://docs.encypherai.com)

</div>
