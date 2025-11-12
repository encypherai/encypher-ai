# 🚀 EncypherAI Commercial - Quick Start Guide

**Welcome to the EncypherAI Commercial Suite!**

This guide will get you up and running in **15 minutes**.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.9+** installed
- ✅ **Node.js 18+** installed (for web apps)
- ✅ **UV** package manager ([install guide](https://github.com/astral-sh/uv))
- ✅ **Git** for version control
- ✅ **PostgreSQL** (for services/API)
- ✅ **Code editor** (VS Code recommended)

---

## 🎯 Choose Your Path

### 🔧 Path 1: CLI Tools (Easiest)
**Time**: 5 minutes  
**Best for**: Testing, auditing, policy validation

### 🌐 Path 2: Web Applications
**Time**: 10 minutes  
**Best for**: Frontend development, dashboards

### 🚀 Path 3: Enterprise API
**Time**: 15 minutes  
**Best for**: Backend development, API integration

### 🔧 Path 4: Microservices
**Time**: 20 minutes  
**Best for**: Full-stack development, architecture

---

## 🔧 Path 1: CLI Tools (5 minutes)

### Option A: Audit Log CLI

```bash
# 1. Navigate to the tool
cd audit_log_cli

# 2. Install dependencies
uv sync

# 3. Run example
uv run python app/main.py generate-report \
  --target ../examples/sample_with_metadata.txt \
  --output report.csv \
  --verbose

# 4. View report
cat report.csv
```

**✅ Success!** You've scanned a file and generated a report.

**Next Steps:**
- Read [audit_log_cli/README.md](./audit_log_cli/README.md)
- Check [audit_log_cli/agents.md](./audit_log_cli/agents.md) for known issues

### Option B: Policy Validator CLI

```bash
# 1. Navigate to the tool
cd policy_validator_cli

# 2. Install dependencies
uv sync

# 3. Run example
uv run python -m policy_validator_cli.app.main validate-metadata \
  --input ../examples/ \
  --policy sample.policy.json \
  --output validation_report.csv \
  --verbose

# 4. View report
cat validation_report.csv
```

**✅ Success!** You've validated files against a policy.

**Next Steps:**
- Read [policy_validator_cli/README.md](./policy_validator_cli/README.md)
- Create custom policies

---

## 🌐 Path 2: Web Applications (10 minutes)

### Option A: Marketing Site

```bash
# 1. Navigate to the app
cd apps/marketing-site

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev

# 4. Open browser
# Visit: http://localhost:3000
```

**✅ Success!** Marketing site is running.

**Next Steps:**
- Read [apps/marketing-site/README.md](./apps/marketing-site/README.md)
- Explore [packages/design-system/](./packages/design-system/)

### Option B: Dashboard

```bash
# 1. Navigate to the app
cd apps/dashboard

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev

# 4. Open browser
# Visit: http://localhost:3001
```

**✅ Success!** Dashboard is running.

**Next Steps:**
- Read [apps/dashboard/README.md](./apps/dashboard/README.md)
- Configure authentication

---

## 🚀 Path 3: Enterprise API (15 minutes)

```bash
# 1. Navigate to the API
cd enterprise_api

# 2. Set up environment
cp .env.example .env
# Edit .env with your database URL and secrets

# 3. Install dependencies
uv sync

# 4. Initialize database
uv run python scripts/init_db.py

# 5. Run the API
uv run uvicorn app.main:app --reload --port 9000

# 6. Test the API
# Visit: http://localhost:9000/docs
```

**✅ Success!** Enterprise API is running with Swagger docs.

**Next Steps:**
- Read [enterprise_api/README.md](./enterprise_api/README.md)
- Check [enterprise_api/docs/API.md](./enterprise_api/docs/API.md)
- Review [enterprise_api/agents.md](./enterprise_api/agents.md)

### Quick API Test

```bash
# Test health endpoint
curl http://localhost:9000/health

# Expected response:
# {"status":"healthy","service":"enterprise-api"}
```

### Verify Provenance with the SDK CLI

```bash
# 1. Jump into the SDK package
cd ../enterprise_sdk
uv sync

# 2. Export an API key (or use ENCYPHER_API_KEY env var)
export ENCYPHER_API_KEY="encypher_live_..."

# 3. Verify an embedded snippet
uv run encypher verify-sentence --file ../examples/signed_snippet.txt

# 4. Inspect a Merkle tree + proof
uv run encypher merkle-tree root_123
uv run encypher merkle-proof root_123 --leaf-index 5

# 5. Stream signing progress from the API
uv run encypher stream-sign --file ../examples/live_article.txt --document-title "Town Hall"

# 6. Encode invisibly at sentence-level (Python REPL)
python - <<'PY'
from encypher_enterprise import EncypherClient
client = EncypherClient(api_key="encypher_live_...")

response = client.sign_with_embeddings(
    text="Breaking news paragraph. Second sentence.",
    document_id="article_demo_01",
    segmentation_level="sentence",
    metadata={"title": "Breaking News", "author": "Jane Reporter"},
)

print("Merkle root:", response.merkle_tree.root_hash)
print("Embedded preview:", response.embedded_content[:120])
PY
```

---

## 🔧 Path 4: Microservices (20 minutes)

### Start All Services with Docker Compose

```bash
# 1. Navigate to services
cd services

# 2. Start all services
docker-compose -f docker-compose.dev.yml up --build

# Services will start on:
# - Auth Service: http://localhost:8001
# - Key Service: http://localhost:8004
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

**✅ Success!** All services are running.

### Test Auth Service

```bash
# Health check
curl http://localhost:8001/health

# Create user
curl -X POST http://localhost:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "name": "Test User"
  }'
```

**Next Steps:**
- Read [services/README.md](./services/README.md)
- Check [services/auth-service/README.md](./services/auth-service/README.md)
- Review [services/auth-service/agents.md](./services/auth-service/agents.md)

---

## 📚 Essential Documentation

### Must Read (15 minutes)
1. [README.md](./README.md) - Repository overview **(5 min)**
2. [AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md) - Quick summary **(3 min)**
3. [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Navigation guide **(7 min)**

### For Your Component (10 minutes)
1. Component's `README.md` - Usage guide **(5 min)**
2. Component's `agents.md` - Development constraints **(5 min)**

### Deep Dive (30+ minutes)
1. [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) - Complete audit **(15 min)**
2. [services/README.md](./services/README.md) - Architecture **(10 min)**
3. [enterprise_api/README.md](./enterprise_api/README.md) - API reference **(15 min)**

---

## 🛠️ Development Workflow

### Daily Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Navigate to your component
cd <component-directory>

# 3. Sync dependencies (Python)
uv sync

# OR install dependencies (Node.js)
npm install

# 4. Run tests
uv run pytest  # Python
npm test       # Node.js

# 5. Start development
uv run uvicorn app.main:app --reload  # API
npm run dev                            # Web app

# 6. Make changes and commit
git add .
git commit -m "feat: add new feature"
git push origin feature-branch
```

### Package Management (Python)

**ALWAYS use UV:**

```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --dev pytest

# Remove dependency
uv remove package-name

# Sync environment
uv sync

# NEVER edit pyproject.toml directly
# NEVER use pip commands
```

---

## 🧪 Testing

### Python Projects

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test
uv run pytest tests/test_main.py -v
```

### JavaScript Projects

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test
npm test -- ComponentName
```

---

## 🐛 Troubleshooting

### Common Issues

#### "uv: command not found"
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### "Database connection failed"
```bash
# Check PostgreSQL is running
psql -h localhost -U postgres -l

# Check connection string in .env
cat .env | grep DATABASE_URL
```

#### "Port already in use"
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
```

#### "Module not found"
```bash
# Python: Sync dependencies
uv sync

# Node.js: Reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📞 Getting Help

### Documentation
- **Quick Reference**: [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)
- **Audit Report**: [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md)
- **Component Guides**: Check component's `agents.md`

### Known Issues
- **audit_log_cli**: Has code issues (see [agents.md](./audit_log_cli/agents.md))
- All other components are production-ready

### Support Channels
- **Internal Team**: Slack #encypher-dev
- **Enterprise**: enterprise@encypherai.com
- **API Issues**: api@encypherai.com

---

## 🎓 Learning Resources

### Video Tutorials (Coming Soon)
- Setting up development environment
- Building your first CLI tool
- Creating a microservice
- Deploying to production

### Code Examples
- [examples/](./examples/) - Usage examples
- [enterprise_sdk/examples/](./enterprise_sdk/examples/) - SDK examples
- Component test files - Testing patterns

### Architecture Diagrams
- [services/README.md](./services/README.md) - Microservices diagram
- [docs/architecture/](./docs/architecture/) - System architecture

---

## ✅ Checklist: First Day Setup

### Environment Setup
- [ ] Install Python 3.9+
- [ ] Install Node.js 18+
- [ ] Install UV package manager
- [ ] Install PostgreSQL
- [ ] Install Redis (optional)
- [ ] Clone repository
- [ ] Read README.md

### Choose Your Component
- [ ] Decide which component to work on
- [ ] Read component's README.md
- [ ] Read component's agents.md
- [ ] Set up component environment
- [ ] Run component tests
- [ ] Start development server

### First Contribution
- [ ] Create feature branch
- [ ] Make small change
- [ ] Run tests
- [ ] Commit changes
- [ ] Create pull request

---

## 🚀 Next Steps

### Week 1: Explore
- [ ] Try all CLI tools
- [ ] Run web applications
- [ ] Test Enterprise API
- [ ] Explore microservices

### Week 2: Deep Dive
- [ ] Read all component READMEs
- [ ] Review architecture docs
- [ ] Study code patterns
- [ ] Run full test suites

### Week 3: Contribute
- [ ] Pick a component
- [ ] Find an issue or feature
- [ ] Implement changes
- [ ] Submit pull request

---

## 🎯 Success Criteria

You're ready to contribute when you can:

- ✅ Run any component locally
- ✅ Understand the architecture
- ✅ Run and write tests
- ✅ Follow development workflows
- ✅ Use UV for package management
- ✅ Navigate documentation easily

---

## 📊 Component Status Overview

| Component | Status | Time to Setup | Difficulty |
|-----------|--------|---------------|------------|
| audit_log_cli | ✅ Functional | 5 min | Easy |
| policy_validator_cli | ✅ Ready | 5 min | Easy |
| apps/marketing-site | ✅ Active | 10 min | Medium |
| apps/dashboard | ✅ Active | 10 min | Medium |
| dashboard_app | ✅ Ready | 15 min | Medium |
| enterprise_api | ✅ Production | 15 min | Hard |
| enterprise_sdk | ✅ Production | 5 min | Medium |
| services/auth-service | ✅ Active | 20 min | Hard |
| shared_commercial_libs | ✅ Ready | 5 min | Easy |
| packages/design-system | ✅ Ready | 10 min | Medium |

---

## 🎉 You're All Set!

You now have:
- ✅ Development environment set up
- ✅ Component running locally
- ✅ Documentation at your fingertips
- ✅ Understanding of workflows

**Happy Coding! 🚀**

---

**Questions?** Check [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) for navigation help.

**Issues?** See component's `agents.md` for troubleshooting.

**Ready to contribute?** Read [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) for guidelines.
