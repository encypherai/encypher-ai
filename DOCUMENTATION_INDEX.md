# Encypher Commercial - Documentation Index

**Last Updated**: March 21, 2026
**Repository**: encypherai-commercial
**Documentation Status**: Complete and Current

---

## Quick Start

### New to the Repository?
1. **Start Here**: [README.md](./README.md) - Repository overview, product tiers, getting started
2. **Feature Matrix**: [FEATURE_MATRIX.md](./FEATURE_MATRIX.md) - Complete feature list by tier
3. **Pricing Strategy**: [docs/pricing/PRICING_STRATEGY.md](./docs/pricing/PRICING_STRATEGY.md) - Strategy, economics, GTM

### Looking for Something Specific?
Use this index to jump directly to the documentation you need.

---

## Documentation by Category

### Root Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](./README.md) | Repository overview, structure, getting started | Everyone |
| [FEATURE_MATRIX.md](./FEATURE_MATRIX.md) | **Master feature list by tier (Free + Enterprise + Add-ons)** | Everyone |
| [MICROSERVICES_FEATURES.md](./MICROSERVICES_FEATURES.md) | Complete feature matrix for all 8 services | Everyone |
| [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) | This file - navigation guide | Everyone |
| [CHANGELOG.md](./CHANGELOG.md) | Version history and changes | Developers |
| [LICENSE](./LICENSE) | Proprietary license information | Legal, Management |
| [docs/api/ERROR_CODES.md](./docs/api/ERROR_CODES.md) | Canonical API error codes and descriptions | Developers, Support |
| [docs/pricing/PRICING_STRATEGY.md](./docs/pricing/PRICING_STRATEGY.md) | Pricing strategy, tiers, coalition economics, OEM guidelines | Product, Marketing, Sales |

---

### CLI Tools

#### Audit Log CLI
| Document | Purpose |
|----------|---------|
| [audit_log_cli/README.md](./audit_log_cli/README.md) | Setup, usage, API reference |
| [audit_log_cli/agents.md](./audit_log_cli/agents.md) | **Development guide, known issues, constraints** |
| [audit_log_cli/pyproject.toml](./audit_log_cli/pyproject.toml) | Dependencies (has duplicates - see agents.md) |

**Key Features**: Scan files, validate metadata, generate CSV reports, trusted signers
**Status**: Functional (needs refactoring - see agents.md)
**Tier**: Free

#### Policy Validator CLI
| Document | Purpose |
|----------|---------|
| [policy_validator_cli/README.md](./policy_validator_cli/README.md) | Setup, usage, policy schemas |
| [policy_validator_cli/agents.md](./policy_validator_cli/agents.md) | **Development guide, best practices** |
| [policy_validator_cli/sample.policy.json](./policy_validator_cli/sample.policy.json) | Example policy file |

**Key Features**: Policy validation, JSON schemas, compliance checking
**Status**: Production Ready
**Tier**: Free

---

### Web Applications

#### Marketing Site
| Document | Purpose |
|----------|---------|
| [apps/marketing-site/README.md](./apps/marketing-site/README.md) | Setup, development, deployment |

**Domain**: `encypher.com`
**Tech**: Next.js, React, Tailwind CSS
**Status**: Active

#### Dashboard
| Document | Purpose |
|----------|---------|
| [apps/dashboard/README.md](./apps/dashboard/README.md) | Setup, features, deployment |
| [PRDs/dashboard_enhancements.md](./PRDs/dashboard_enhancements.md) | Dashboard enhancement PRD |

**Domain**: `dashboard.encypher.com`
**Tech**: Next.js, React, Tailwind CSS
**Features**: API key management, usage tracking, team management, webhooks, notifications, command palette, dark mode, CSV export
**Status**: Active (Enhanced November 2025)

#### Compliance Dashboard
| Document | Purpose |
|----------|---------|
| [dashboard_app/README.md](./dashboard_app/README.md) | Architecture, setup, directory signing |
| [dashboard_app/backend/](./dashboard_app/backend/) | FastAPI backend |
| [dashboard_app/frontend/](./dashboard_app/frontend/) | Next.js frontend |

**Purpose**: Enterprise compliance, directory signing, verification
**Tech**: FastAPI + Next.js
**Status**: Production Ready
**Tier**: Enterprise

---

### Enterprise Products

#### Enterprise API
| Document | Purpose |
|----------|---------|
| [enterprise_api/README.md](./enterprise_api/README.md) | **Complete API reference** (653 lines) |
| [enterprise_api/agents.md](./enterprise_api/agents.md) | **Development guide, deployment** (612 lines) |
| [enterprise_api/docs/API.md](./enterprise_api/docs/API.md) | Detailed API documentation |
| [enterprise_api/docs/THREAT_MODEL.md](./enterprise_api/docs/THREAT_MODEL.md) | Threat model for enterprise archive workflows |
| [enterprise_api/docs/KEY_MANAGEMENT_READINESS.md](./enterprise_api/docs/KEY_MANAGEMENT_READINESS.md) | Key management rotation, revocation, KMS readiness |
| [enterprise_api/docs/PRIVACY_RETENTION_POLICY.md](./enterprise_api/docs/PRIVACY_RETENTION_POLICY.md) | Engineering retention and deletion policy |
| [enterprise_api/docs/SECURITY_REVIEW_CHECKLIST.md](./enterprise_api/docs/SECURITY_REVIEW_CHECKLIST.md) | SOC2/GDPR security review checklist |
| [enterprise_api/docs/RELIABILITY_RESILIENCE.md](./enterprise_api/docs/RELIABILITY_RESILIENCE.md) | Reliability and resilience strategy (HA, idempotency, retries) |
| [enterprise_api/docs/PERFORMANCE_SCALE.md](./enterprise_api/docs/PERFORMANCE_SCALE.md) | Performance targets and scale planning |
| [enterprise_api/docs/OBSERVABILITY_INCIDENT_RESPONSE.md](./enterprise_api/docs/OBSERVABILITY_INCIDENT_RESPONSE.md) | Observability and incident response plan |
| [enterprise_api/docs/DATA_INTEGRITY_AUDITABILITY.md](./enterprise_api/docs/DATA_INTEGRITY_AUDITABILITY.md) | Data integrity and auditability strategy |
| [enterprise_api/docs/RELEASE_READINESS.md](./enterprise_api/docs/RELEASE_READINESS.md) | Staging parity and release readiness checklist |
| [enterprise_api/docs/API_CONTRACT_CLIENT_READINESS.md](./enterprise_api/docs/API_CONTRACT_CLIENT_READINESS.md) | OpenAPI contract + SDK readiness checklist |
| [enterprise_api/docs/USAGE_ANALYTICS_REPORTING.md](./enterprise_api/docs/USAGE_ANALYTICS_REPORTING.md) | Usage analytics and customer reporting plan |
| [enterprise_api/docs/TESTING_VALIDATION.md](./enterprise_api/docs/TESTING_VALIDATION.md) | Testing and validation checklist |
| [enterprise_api/docs/DISASTER_RECOVERY_RUNBOOK.md](./enterprise_api/docs/DISASTER_RECOVERY_RUNBOOK.md) | Disaster recovery runbook |
| [enterprise_api/docs/DEPLOYMENT.md](./enterprise_api/docs/DEPLOYMENT.md) | Deployment guide |
| [enterprise_api/docs/QUICKSTART.md](./enterprise_api/docs/QUICKSTART.md) | Quick start guide |
| [enterprise_api/docs/LICENSING_API.md](./enterprise_api/docs/LICENSING_API.md) | Licensing API reference (agreements, content, payouts) |
| [docs/perf/batch-sign.md](./docs/perf/batch-sign.md) | Batch throughput benchmark results |

**Key Features**: C2PA signing, verification, Merkle trees, plagiarism detection, CDN provenance continuity, audio C2PA signing (WAV, MP3, M4A/AAC), video C2PA signing (MP4, MOV, M4V, AVI), live video stream signing (C2PA 2.3 Section 19)
**Status**: Production Ready
**Tier**: Enterprise
**Port**: 9000

#### Audio C2PA Signing

Audio signing has no standalone guide -- the implementation is self-documenting via the shared C2PA module pattern. Key files:

| Document | Purpose |
|----------|---------|
| `enterprise_api/app/services/audio_signing_service.py` | Audio signing service (passthrough + C2PA) |
| `enterprise_api/app/services/audio_verification_service.py` | Audio verification (delegates to shared verifier) |
| `enterprise_api/app/services/audio_signing_executor.py` | Per-org credential loading and orchestration |
| `enterprise_api/app/api/v1/enterprise/audio_attribution.py` | REST endpoints (`/enterprise/audio/sign`, `/enterprise/audio/verify`) |
| `enterprise_api/app/utils/audio_utils.py` | Format detection, MIME canonicalization, validation |

**Supported Formats**: WAV (RIFF), MP3 (ID3), M4A/AAC (ISO BMFF)
**Status**: Production Ready
**Tier**: Enterprise
**Tests**: 51 tests (35 in test_audio_signing.py + 16 in test_c2pa_shared.py)

#### Video C2PA Signing

Video signing follows the same shared C2PA module pattern as audio. Key differences: multipart upload (not base64), 500 MB max, large file download endpoint. Key files:

| Document | Purpose |
|----------|---------|
| `enterprise_api/app/services/video_signing_service.py` | Video signing service (passthrough + C2PA) |
| `enterprise_api/app/services/video_verification_service.py` | Video verification (delegates to shared verifier) |
| `enterprise_api/app/services/video_signing_executor.py` | Per-org credential loading and orchestration |
| `enterprise_api/app/api/v1/enterprise/video_attribution.py` | REST endpoints (`/enterprise/video/sign`, `/enterprise/video/verify`, `/enterprise/video/download/{video_id}`) |
| `enterprise_api/app/utils/video_utils.py` | Format detection (ftyp, RIFF+AVI, EBML), MIME canonicalization, validation |

**Supported Formats**: MP4, MOV, M4V (ISO BMFF), AVI (RIFF). WebM/MKV detected and rejected.
**Status**: Production Ready
**Tier**: Enterprise
**Tests**: 34 tests in test_video_signing.py + shared tests in test_c2pa_shared.py

#### Live Video Stream Signing (C2PA 2.3 Section 19)

Per-segment C2PA manifest signing for live video streams with backwards-linked provenance chain and Merkle root computation. Key files:

| Document | Purpose |
|----------|---------|
| `enterprise_api/app/services/video_stream_signing_service.py` | Session management, segment signing, Merkle root |
| `enterprise_api/app/api/v1/enterprise/video_stream_attribution.py` | REST endpoints (start, segment, finalize, status) |

**Status**: Production Ready
**Tier**: Enterprise
**Tests**: 17 tests in test_video_stream_signing.py

#### CDN Provenance Continuity
| Document | Purpose |
|----------|---------|
| [docs/c2pa/CDN_PROVENANCE_CONTINUITY.md](./docs/c2pa/CDN_PROVENANCE_CONTINUITY.md) | **Technical reference** — architecture, API endpoints, verification states, CDN integrations |
| [PRDs/CURRENT/PRD_CDN_Provenance_Continuity.md](./PRDs/CURRENT/PRD_CDN_Provenance_Continuity.md) | Product requirements and WBS task list |
| [integrations/cloudflare-workers/](./integrations/cloudflare-workers/) | Cloudflare Worker + wrangler config template |
| [integrations/fastly-compute/](./integrations/fastly-compute/) | Fastly Compute@Edge (Rust) |
| [integrations/lambda-edge/](./integrations/lambda-edge/) | Lambda@Edge viewer-response handler (Node.js) |

**Key Features**: pHash-based manifest sidecar, three-state verification, CF/Fastly/Lambda@Edge workers, WordPress + Ghost image signing, CBOR manifests, analytics dashboard
**Status**: Production Ready (Phase 1-3 complete)
**Tier**: Enterprise
**Tests**: 36 pytest tests passing

#### Enterprise SDKs
| Document | Purpose |
|----------|---------|
| [sdk/README.md](./sdk/README.md) | **Auto-generated SDKs** (Python/TypeScript/Go/Rust) |
| [sdk/python/](./sdk/python/) | Python SDK (auto-generated from OpenAPI) |
| [sdk/typescript/](./sdk/typescript/) | TypeScript SDK (auto-generated from OpenAPI) |
| [sdk/go/](./sdk/go/) | Go SDK (auto-generated from OpenAPI) |
| [sdk/rust/](./sdk/rust/) | Rust SDK (auto-generated from OpenAPI) |
| [archive/enterprise_sdk_deprecated/DEPRECATED.md](./archive/enterprise_sdk_deprecated/DEPRECATED.md) | Deprecation notice for the archived hand-crafted SDK |

**Key Features**: Auto-generated from API spec, always in sync, MIT licensed
**Status**: Generated (not yet published to registries)
**Tier**: Enterprise
**API Docs**: [api.encypher.com/docs](https://api.encypher.com/docs)

---

### Microservices

#### Services Overview
| Document | Purpose |
|----------|---------|
| [services/README.md](./services/README.md) | **Microservices architecture** |
| [services/ENV_VARS_MAPPING.md](./services/ENV_VARS_MAPPING.md) | Environment variables mapping |
| [docker-compose.microservices.yml](./docker-compose.microservices.yml) | Full microservices stack |

**Architecture**: 8 core services plus the Enterprise API
**Status**: Active

#### Active Services
| Document | Purpose |
|----------|---------|
| [services/web-service/](./services/web-service/) | Marketing forms, demo requests, analytics |
| [services/user-service/](./services/user-service/) | User profiles, teams, preferences, organization management |
| [services/key-service/](./services/key-service/) | API key management and organization-scoped credentials |
| [services/encoding-service/](./services/encoding-service/) | Signing and metadata embedding workflows |
| [services/verification-service/](./services/verification-service/) | Verification and tamper-detection workflows |
| [services/analytics-service/](./services/analytics-service/) | Usage metrics and reporting |
| [services/billing-service/](./services/billing-service/) | Billing, subscriptions, and Stripe integration |
| [services/notification-service/](./services/notification-service/) | Email and notification delivery |

**See also**: [README.md](./README.md#-microservices-architecture) and [services/README.md](./services/README.md) for the current service inventory and ports.

---

### Integrations

#### WordPress Plugin
| Document | Purpose |
|----------|---------|
| [integrations/wordpress-provenance-plugin/README.md](./integrations/wordpress-provenance-plugin/README.md) | Installation, configuration, Docker setup |

**Features**: Gutenberg & Classic editor integration, Enterprise API calls
**Status**: Production Ready

---

### Shared Libraries

#### Commercial Shared Library
| Document | Purpose |
|----------|---------|
| [shared_commercial_libs/README.md](./shared_commercial_libs/README.md) | High-level API, utilities |
| [shared_commercial_libs/agents.md](./shared_commercial_libs/agents.md) | **Development guide** (580 lines) |

**Purpose**: Shared Python library for all commercial tools
**Status**: Production Ready
**Used By**: audit_log_cli, dashboard_app

#### Design System
| Document | Purpose |
|----------|---------|
| [packages/design-system/README.md](./packages/design-system/README.md) | **Component library** (395 lines) |
| [packages/design-system/IMPLEMENTATION_GUIDE.md](./packages/design-system/IMPLEMENTATION_GUIDE.md) | Implementation guide |

**Purpose**: Unified React/TypeScript components for all web properties
**Status**: Production Ready
**Used By**: All web applications

---

### Architecture & Planning

#### Architecture Documentation
| Document | Purpose |
|----------|---------|
| [docs/architecture/BACKEND_ARCHITECTURE.md](./docs/architecture/BACKEND_ARCHITECTURE.md) | Backend system design |
| [docs/architecture/EMBEDDING_MODES.md](./docs/architecture/EMBEDDING_MODES.md) | **Comprehensive reference for all embedding modes** - VS256, VS256+RS, ZW, C2PA - with platform compatibility, PDF behavior, security, and API usage |
| [docs/architecture/MINIMAL_UUID_EMBEDDING_FLOW.html](./docs/architecture/MINIMAL_UUID_EMBEDDING_FLOW.html) | HTML diagram of minimal_uuid signing + verification flow |
| [docs/architecture/EMBEDDING_ICON_DEMO.html](./docs/architecture/EMBEDDING_ICON_DEMO.html) | Interactive article demo with embedding icons + payload details |
| [docs/architecture/SUBDOMAIN_STRATEGY.md](./docs/architecture/SUBDOMAIN_STRATEGY.md) | Domain strategy |
| [docs/architecture/CORRECTED_MIGRATION_PLAN.md](./docs/architecture/CORRECTED_MIGRATION_PLAN.md) | Migration planning |

#### Implementation Plans
| Document | Purpose |
|----------|---------|
| [docs/implementation_plans/](./docs/implementation_plans/) | Phase plans, progress tracking |
| [docs/implementation_plans/comprehensive_plan_api.md](./docs/implementation_plans/comprehensive_plan_api.md) | API implementation plan |

#### Product Requirements
| Document | Purpose |
|----------|---------|
| [PRDs/CURRENT/](./PRDs/CURRENT/) | Active PRDs |
| [PRDs/CURRENT/PRD_Enterprise_API_Production_Readiness_Blockers.md](./PRDs/CURRENT/PRD_Enterprise_API_Production_Readiness_Blockers.md) | Production readiness blockers for enterprise API |
| [PRDs/CURRENT/PRD_Enterprise_API_Mypy_Errors_Overview.md](./PRDs/CURRENT/PRD_Enterprise_API_Mypy_Errors_Overview.md) | Mypy error inventory and remediation plan |
| [PRDs/CURRENT/PRD_Python_SDK_WBS.md](./PRDs/CURRENT/PRD_Python_SDK_WBS.md) | Python SDK production readiness WBS |
| [docs/PRD.md](./docs/PRD.md) | Main product requirements |

#### C2PA Reference
| Document | Purpose |
|----------|---------|
| [docs/c2pa/Manifests_Text.adoc](./docs/c2pa/Manifests_Text.adoc) | C2PA 2.2 text manifest specification |
| [docs/c2pa/C2PA_2.3_CONFORMANCE_CHECKLIST.md](./docs/c2pa/C2PA_2.3_CONFORMANCE_CHECKLIST.md) | C2PA 2.3 conformance checklist + evidence references |
| [docs/c2pa/C2PA_2.3_EVIDENCE_BUNDLE.md](./docs/c2pa/C2PA_2.3_EVIDENCE_BUNDLE.md) | C2PA 2.3 submission evidence bundle |

---

### Examples & Scripts

#### Examples
| Document | Purpose |
|----------|---------|
| [examples/README.md](./examples/README.md) | Usage examples |
| [examples/run_audit_example.ps1](./examples/run_audit_example.ps1) | Audit CLI example |

#### Scripts
| Document | Purpose |
|----------|---------|
| [scripts/setup_dev_env.ps1](./scripts/setup_dev_env.ps1) | Development environment setup |
| [scripts/repo_stats.py](./scripts/repo_stats.py) | Repository statistics |
| [scripts/generate_sdk_files.py](./scripts/generate_sdk_files.py) | SDK file generation |

---

## Documentation by Role

### For New Developers
**Start Here:**
1. [README.md](./README.md) - Repository overview
2. [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Documentation map
3. Explore directory structure
4. Set up development environment

**Essential Reading:**
- [services/README.md](./services/README.md) - Microservices architecture
- [shared_commercial_libs/agents.md](./shared_commercial_libs/agents.md) - Shared library guide

### For Frontend Developers
**Essential:**
- [packages/design-system/README.md](./packages/design-system/README.md) - Component library
- [apps/marketing-site/README.md](./apps/marketing-site/README.md) - Marketing site
- [apps/dashboard/README.md](./apps/dashboard/README.md) - Dashboard app

### For Backend Developers
**Essential:**
- [enterprise_api/README.md](./enterprise_api/README.md) - API reference
- [enterprise_api/agents.md](./enterprise_api/agents.md) - Development guide
- [services/README.md](./services/README.md) - Microservices
- [services/auth-service/agents.md](./services/auth-service/agents.md) - Auth service

### For DevOps/SRE
**Essential:**
- [enterprise_api/docs/DEPLOYMENT.md](./enterprise_api/docs/DEPLOYMENT.md) - Deployment
- [services/README.md](./services/README.md) - Service architecture
- [services/docker-compose.dev.yml](./services/docker-compose.dev.yml) - Docker setup

### For Product Managers
**Essential:**
- [README.md](./README.md) - Product tiers, features
- [FEATURE_MATRIX.md](./FEATURE_MATRIX.md) - Feature and tier reference
- [PRDs/CURRENT/](./PRDs/CURRENT/) - Product requirements
- Component READMEs - Feature capabilities

### For QA/Testing
**Essential:**
- Component `agents.md` files - Testing strategies
- [enterprise_api/agents.md](./enterprise_api/agents.md) - API testing
- [docs/testing_guide.md](./docs/testing_guide.md) - Testing guide

---

## Finding Documentation

### By Technology

#### Python Projects
- [audit_log_cli/](./audit_log_cli/)
- [policy_validator_cli/](./policy_validator_cli/)
- [enterprise_api/](./enterprise_api/)
- [sdk/](./sdk/)
- [shared_commercial_libs/](./shared_commercial_libs/)
- [services/auth-service/](./services/auth-service/)
- [services/key-service/](./services/key-service/)

#### JavaScript/TypeScript Projects
- [apps/marketing-site/](./apps/marketing-site/)
- [apps/dashboard/](./apps/dashboard/)
- [dashboard_app/frontend/](./dashboard_app/frontend/)
- [packages/design-system/](./packages/design-system/)

#### Full-Stack Projects
- [dashboard_app/](./dashboard_app/) - FastAPI + Next.js

### By Feature

#### Authentication
- [services/auth-service/](./services/auth-service/) - JWT, OAuth
- [enterprise_api/](./enterprise_api/) - API key auth

#### Content Signing
- [enterprise_api/](./enterprise_api/) - C2PA signing
- **[Enterprise SDKs](./sdk/README.md)** - Auto-generated SDKs (Python/TypeScript/Go/Rust)
- [integrations/wordpress-provenance-plugin/](./integrations/wordpress-provenance-plugin/) - WordPress

#### Verification
- [audit_log_cli/](./audit_log_cli/) - CLI verification
- [enterprise_api/](./enterprise_api/) - API verification
- [shared_commercial_libs/](./shared_commercial_libs/) - Shared verification

#### Policy Management
- [policy_validator_cli/](./policy_validator_cli/) - Policy validation

#### UI Components
- [packages/design-system/](./packages/design-system/) - Component library

---

## Documentation Quality

### Excellent Documentation (9-10/10)
- [enterprise_api/](./enterprise_api/) - 653-line README + agents.md
- [sdk/](./sdk/) - Auto-generated SDKs (Python/TypeScript/Go/Rust)
- [packages/design-system/](./packages/design-system/) - 395-line component guide
- [services/README.md](./services/README.md) - Complete architecture

### Good Documentation (7-8/10)
- [audit_log_cli/](./audit_log_cli/) - Good README, agents.md with issues
- [policy_validator_cli/](./policy_validator_cli/) - Clean, well-documented
- [dashboard_app/](./dashboard_app/) - Comprehensive setup guide
- [shared_commercial_libs/](./shared_commercial_libs/) - High-level API guide
- [services/auth-service/](./services/auth-service/) - Complete service guide

### Adequate Documentation (6-7/10)
- [apps/marketing-site/](./apps/marketing-site/) - Basic but sufficient
- [apps/dashboard/](./apps/dashboard/) - Basic but sufficient
- [integrations/wordpress-provenance-plugin/](./integrations/wordpress-provenance-plugin/) - Good setup guide

---

## Documentation Maintenance

### When to Update Documentation

#### Always Update When:
- Adding new features
- Changing APIs
- Modifying configuration
- Adding dependencies
- Changing architecture

#### Update These Files:
1. Component's `README.md` - Usage changes
2. Component's `agents.md` - Development changes
3. Root `README.md` - New components
4. `DOCUMENTATION_INDEX.md` - New documentation

### Documentation Review Schedule
- **Weekly**: Check for outdated information
- **Monthly**: Review all READMEs
- **Quarterly**: Full documentation review
- **After Major Changes**: Immediate update

---

## Getting Help

### Documentation Issues
- Check component's `agents.md` for known issues
- Check [docs/archive/README.md](./docs/archive/README.md) for historical documentation
- File issue in repository

### Development Questions
- Check component's `agents.md` for constraints
- Review component's `README.md` for usage
- Check `services/README.md` for architecture

### Architecture Questions
- Review [docs/architecture/](./docs/architecture/)
- Check [services/README.md](./services/README.md)
- Review component integration points

---

## Learning Path

### Week 1: Repository Basics
1. Read [README.md](./README.md)
2. Read [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)
3. Explore directory structure
4. Set up development environment

### Week 2: Choose Your Path

#### CLI Tools Path
1. [audit_log_cli/README.md](./audit_log_cli/README.md)
2. [audit_log_cli/agents.md](./audit_log_cli/agents.md)
3. [policy_validator_cli/README.md](./policy_validator_cli/README.md)
4. [shared_commercial_libs/README.md](./shared_commercial_libs/README.md)

#### API Development Path
1. [enterprise_api/README.md](./enterprise_api/README.md)
2. [enterprise_api/agents.md](./enterprise_api/agents.md)
3. [enterprise_api/docs/API.md](./enterprise_api/docs/API.md)
4. [services/README.md](./services/README.md)

#### Frontend Path
1. [packages/design-system/README.md](./packages/design-system/README.md)
2. [apps/marketing-site/README.md](./apps/marketing-site/README.md)
3. [apps/dashboard/README.md](./apps/dashboard/README.md)
4. [dashboard_app/README.md](./dashboard_app/README.md)

### Week 3+: Deep Dive
- Read component-specific `agents.md` files
- Review architecture documentation
- Study implementation plans
- Contribute to codebase

---

## Documentation Statistics

- **Historical documents**: See [docs/archive/README.md](./docs/archive/README.md)
- **Active PRDs**: See [PRDs/CURRENT/](./PRDs/CURRENT/)
- **Archived PRDs**: See [PRDs/ARCHIVE/](./PRDs/ARCHIVE/)
- **Primary sources of truth**: [README.md](./README.md), [FEATURE_MATRIX.md](./FEATURE_MATRIX.md), and component READMEs

---

## Quick Links

### Most Important Documents
1. [README.md](./README.md) - Start here
2. [FEATURE_MATRIX.md](./FEATURE_MATRIX.md) - Feature and tier SSOT
3. [services/README.md](./services/README.md) - Architecture
4. [enterprise_api/README.md](./enterprise_api/README.md) - API reference

### Development Guides (agents.md)
- [audit_log_cli/agents.md](./audit_log_cli/agents.md)
- [policy_validator_cli/agents.md](./policy_validator_cli/agents.md)
- [enterprise_api/agents.md](./enterprise_api/agents.md)
- [services/auth-service/agents.md](./services/auth-service/agents.md)
- [shared_commercial_libs/agents.md](./shared_commercial_libs/agents.md)

---

**Last Updated**: February 13, 2026
**Maintained By**: Development Team
**Next Review**: May 13, 2026 (or after major changes)
