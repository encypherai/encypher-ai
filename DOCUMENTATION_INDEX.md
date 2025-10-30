# 📚 EncypherAI Commercial - Documentation Index

**Last Updated**: October 30, 2025  
**Repository**: encypherai-commercial  
**Documentation Status**: ✅ Complete & Current

---

## 🚀 Quick Start

### New to the Repository?
1. **Start Here**: [README.md](./README.md) - Repository overview, product tiers, getting started
2. **Audit Report**: [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) - Complete findings and recommendations
3. **Completion Summary**: [AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md) - Quick reference

### Looking for Something Specific?
Use this index to jump directly to the documentation you need.

---

## 📖 Documentation by Category

### 🏠 Root Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](./README.md) | Repository overview, structure, getting started | Everyone |
| [MICROSERVICES_FEATURES.md](./MICROSERVICES_FEATURES.md) | **Complete feature matrix for all 8 services** | Everyone |
| [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) | Complete audit report with findings | Developers, Managers |
| [AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md) | Quick completion summary | Everyone |
| [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) | This file - navigation guide | Everyone |
| [CHANGELOG.md](./CHANGELOG.md) | Version history and changes | Developers |
| [LICENSE](./LICENSE) | Proprietary license information | Legal, Management |

---

### 🔧 CLI Tools

#### Audit Log CLI
| Document | Purpose |
|----------|---------|
| [audit_log_cli/README.md](./audit_log_cli/README.md) | Setup, usage, API reference |
| [audit_log_cli/agents.md](./audit_log_cli/agents.md) | **Development guide, known issues, constraints** |
| [audit_log_cli/pyproject.toml](./audit_log_cli/pyproject.toml) | Dependencies (⚠️ has duplicates - see agents.md) |

**Key Features**: Scan files, validate metadata, generate CSV reports, trusted signers  
**Status**: ✅ Functional (⚠️ needs refactoring - see agents.md)  
**Tier**: Free/Professional

#### Policy Validator CLI
| Document | Purpose |
|----------|---------|
| [policy_validator_cli/README.md](./policy_validator_cli/README.md) | Setup, usage, policy schemas |
| [policy_validator_cli/agents.md](./policy_validator_cli/agents.md) | **Development guide, best practices** |
| [policy_validator_cli/sample.policy.json](./policy_validator_cli/sample.policy.json) | Example policy file |

**Key Features**: Policy validation, JSON schemas, compliance checking  
**Status**: ✅ Production Ready  
**Tier**: Professional

---

### 🌐 Web Applications

#### Marketing Site
| Document | Purpose |
|----------|---------|
| [apps/marketing-site/README.md](./apps/marketing-site/README.md) | Setup, development, deployment |

**Domain**: `encypherai.com`  
**Tech**: Next.js, React, Tailwind CSS  
**Status**: ✅ Active

#### Dashboard
| Document | Purpose |
|----------|---------|
| [apps/dashboard/README.md](./apps/dashboard/README.md) | Setup, features, deployment |

**Domain**: `dashboard.encypherai.com`  
**Tech**: Next.js, React, Tailwind CSS  
**Features**: API key management, usage tracking  
**Status**: ✅ Active

#### Compliance Dashboard
| Document | Purpose |
|----------|---------|
| [dashboard_app/README.md](./dashboard_app/README.md) | Architecture, setup, directory signing |
| [dashboard_app/backend/](./dashboard_app/backend/) | FastAPI backend |
| [dashboard_app/frontend/](./dashboard_app/frontend/) | Next.js frontend |

**Purpose**: Enterprise compliance, directory signing, verification  
**Tech**: FastAPI + Next.js  
**Status**: ✅ Production Ready  
**Tier**: Enterprise

---

### 🚀 Enterprise Products

#### Enterprise API
| Document | Purpose |
|----------|---------|
| [enterprise_api/README.md](./enterprise_api/README.md) | **Complete API reference** (653 lines) |
| [enterprise_api/agents.md](./enterprise_api/agents.md) | **Development guide, deployment** (612 lines) |
| [enterprise_api/docs/API.md](./enterprise_api/docs/API.md) | Detailed API documentation |
| [enterprise_api/docs/DEPLOYMENT.md](./enterprise_api/docs/DEPLOYMENT.md) | Deployment guide |
| [enterprise_api/docs/QUICKSTART.md](./enterprise_api/docs/QUICKSTART.md) | Quick start guide |

**Key Features**: C2PA signing, verification, Merkle trees, plagiarism detection  
**Status**: ✅ Production Ready  
**Tier**: Enterprise  
**Port**: 9000

#### Enterprise SDK
| Document | Purpose |
|----------|---------|
| [enterprise_sdk/README.md](./enterprise_sdk/README.md) | **Complete SDK guide** (855 lines) |
| [enterprise_sdk/examples/](./enterprise_sdk/examples/) | Usage examples |

**Key Features**: Batch operations, CI/CD integration, LangChain/OpenAI wrappers  
**Status**: ✅ Production Ready  
**Tier**: Enterprise

---

### 🔧 Microservices

#### Services Overview
| Document | Purpose |
|----------|---------|
| [services/README.md](./services/README.md) | **Microservices architecture** (485 lines) |
| [services/docker-compose.dev.yml](./services/docker-compose.dev.yml) | Development environment |

**Architecture**: 9 services (2 active, 7 planned)  
**Status**: 🚧 In Development

#### Auth Service
| Document | Purpose |
|----------|---------|
| [services/auth-service/README.md](./services/auth-service/README.md) | Setup, API endpoints |
| [services/auth-service/agents.md](./services/auth-service/agents.md) | **Development guide** (650 lines) |

**Features**: JWT auth, OAuth (Google/GitHub), session management  
**Status**: ✅ Active  
**Port**: 8001

#### Key Service
| Document | Purpose |
|----------|---------|
| [services/key-service/](./services/key-service/) | Key management service |

**Features**: Cryptographic key management, rotation  
**Status**: 🚧 Partial Implementation  
**Port**: 8004

#### Planned Services
- **api-gateway** (Port 8000) - Central routing, rate limiting
- **user-service** (Port 8002) - User profiles
- **billing-service** (Port 8003) - Subscriptions
- **encoding-service** (Port 8005) - C2PA encoding
- **verification-service** (Port 8006) - Content verification
- **analytics-service** (Port 8007) - Usage analytics
- **notification-service** (Port 8008) - Notifications

---

### 🔌 Integrations

#### WordPress Plugin
| Document | Purpose |
|----------|---------|
| [integrations/wordpress-assurance-plugin/README.md](./integrations/wordpress-assurance-plugin/README.md) | Installation, configuration, Docker setup |

**Features**: Gutenberg & Classic editor integration, Enterprise API calls  
**Status**: ✅ Production Ready

---

### 📦 Shared Libraries

#### Commercial Shared Library
| Document | Purpose |
|----------|---------|
| [shared_commercial_libs/README.md](./shared_commercial_libs/README.md) | High-level API, utilities |
| [shared_commercial_libs/agents.md](./shared_commercial_libs/agents.md) | **Development guide** (580 lines) |

**Purpose**: Shared Python library for all commercial tools  
**Status**: ✅ Production Ready  
**Used By**: audit_log_cli, dashboard_app

#### Design System
| Document | Purpose |
|----------|---------|
| [packages/design-system/README.md](./packages/design-system/README.md) | **Component library** (395 lines) |
| [packages/design-system/IMPLEMENTATION_GUIDE.md](./packages/design-system/IMPLEMENTATION_GUIDE.md) | Implementation guide |

**Purpose**: Unified React/TypeScript components for all web properties  
**Status**: ✅ Production Ready  
**Used By**: All web applications

---

### 📚 Architecture & Planning

#### Architecture Documentation
| Document | Purpose |
|----------|---------|
| [docs/architecture/BACKEND_ARCHITECTURE.md](./docs/architecture/BACKEND_ARCHITECTURE.md) | Backend system design |
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
| [docs/PRD.md](./docs/PRD.md) | Main product requirements |

#### C2PA Reference
| Document | Purpose |
|----------|---------|
| [docs/c2pa/Manifests_Text.adoc](./docs/c2pa/Manifests_Text.adoc) | C2PA 2.2 text manifest specification |

---

### 🧪 Examples & Scripts

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

## 🎯 Documentation by Role

### For New Developers
**Start Here:**
1. [README.md](./README.md) - Repository overview
2. [AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md) - Quick summary
3. Component's `agents.md` - Development constraints
4. Component's `README.md` - Usage instructions

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
- [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) - Audit findings
- [PRDs/CURRENT/](./PRDs/CURRENT/) - Product requirements
- Component READMEs - Feature capabilities

### For QA/Testing
**Essential:**
- Component `agents.md` files - Testing strategies
- [enterprise_api/agents.md](./enterprise_api/agents.md) - API testing
- [docs/testing_guide.md](./docs/testing_guide.md) - Testing guide

---

## 🔍 Finding Documentation

### By Technology

#### Python Projects
- [audit_log_cli/](./audit_log_cli/)
- [policy_validator_cli/](./policy_validator_cli/)
- [enterprise_api/](./enterprise_api/)
- [enterprise_sdk/](./enterprise_sdk/)
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
- [enterprise_sdk/](./enterprise_sdk/) - SDK wrapper
- [integrations/wordpress-assurance-plugin/](./integrations/wordpress-assurance-plugin/) - WordPress

#### Verification
- [audit_log_cli/](./audit_log_cli/) - CLI verification
- [enterprise_api/](./enterprise_api/) - API verification
- [shared_commercial_libs/](./shared_commercial_libs/) - Shared verification

#### Policy Management
- [policy_validator_cli/](./policy_validator_cli/) - Policy validation

#### UI Components
- [packages/design-system/](./packages/design-system/) - Component library

---

## 📊 Documentation Quality

### Excellent Documentation (9-10/10)
- ✅ enterprise_api - 653-line README + agents.md
- ✅ enterprise_sdk - 855-line comprehensive guide
- ✅ packages/design-system - 395-line component guide
- ✅ services/README.md - Complete architecture

### Good Documentation (7-8/10)
- ✅ audit_log_cli - Good README, agents.md with issues
- ✅ policy_validator_cli - Clean, well-documented
- ✅ dashboard_app - Comprehensive setup guide
- ✅ shared_commercial_libs - High-level API guide
- ✅ services/auth-service - Complete service guide

### Adequate Documentation (6-7/10)
- ✅ apps/marketing-site - Basic but sufficient
- ✅ apps/dashboard - Basic but sufficient
- ✅ integrations/wordpress-assurance-plugin - Good setup guide

---

## 🚨 Known Issues

### Critical (Fix Immediately)
1. **audit_log_cli/pyproject.toml** - Duplicate dependencies
   - See: [audit_log_cli/agents.md](./audit_log_cli/agents.md)

2. **audit_log_cli/app/main.py** - Duplicate imports
   - See: [audit_log_cli/agents.md](./audit_log_cli/agents.md)

3. **audit_log_cli/app/main.py** - Incomplete function definition
   - See: [audit_log_cli/agents.md](./audit_log_cli/agents.md)

### No Other Critical Issues
All other components are production-ready.

---

## 🔄 Documentation Maintenance

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
- **Quarterly**: Full audit (like this one)
- **After Major Changes**: Immediate update

---

## 📞 Getting Help

### Documentation Issues
- Check component's `agents.md` for known issues
- Review `DOCUMENTATION_AUDIT.md` for findings
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

## 🎓 Learning Path

### Week 1: Repository Basics
1. Read [README.md](./README.md)
2. Read [AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md)
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

## 📈 Documentation Statistics

- **Total Documentation Files**: 50+
- **New Files Created (This Audit)**: 9
- **Total Lines of Documentation**: 10,000+
- **Components Documented**: 15
- **Coverage**: 100% of active components

---

## ✨ Quick Links

### Most Important Documents
1. [README.md](./README.md) - Start here
2. [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) - Audit report
3. [services/README.md](./services/README.md) - Architecture
4. [enterprise_api/README.md](./enterprise_api/README.md) - API reference

### Development Guides (agents.md)
- [audit_log_cli/agents.md](./audit_log_cli/agents.md)
- [policy_validator_cli/agents.md](./policy_validator_cli/agents.md)
- [enterprise_api/agents.md](./enterprise_api/agents.md)
- [services/auth-service/agents.md](./services/auth-service/agents.md)
- [shared_commercial_libs/agents.md](./shared_commercial_libs/agents.md)

---

**Last Updated**: October 30, 2025  
**Maintained By**: Development Team  
**Next Review**: January 30, 2026 (or after major changes)
