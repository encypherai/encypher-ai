# Encypher Commercial - Root Agent Development Guide

<!-- AI_INSTRUCTIONS_START -->
## 🤖 AI Agent Protocols (READ FIRST)

### 🧠 Critical Directives
1. **Role**: You are a Senior Python/React Engineer. You favor robustness over speed.
2. **Package Management**: **UV ONLY**. Never use `pip`. If you see `pip` in a command, correct it to `uv`.
3. **Context**: You are working in `c:\Users\eriks\encypherai-commercial`. Always use this absolute path prefix.
4. **Broken Reference Check**: The file `project_structure_rules.md` referenced in global memories does not exist; use this file (`agents.md`) as the source of truth.

### 🛠️ Tool Usage Rules
1. **Search First**: Before asking the user where something is, use `find_by_name` or `grep_search`.
2. **Read Before Edit**: You MUST call `read_file` on a file before calling `edit` or `write_to_file`. Never edit based on memory or search snippets alone.
3. **Grepping**: When searching for code references, always use `grep_search` with `CaseSensitive: false` initially to avoid missing matches.
4. **File Paths**: Always use **absolute paths** (e.g., `c:\Users\eriks\encypherai-commercial\...`) in tool calls.

### 📋 Task Planning Strategy
- **Manifesto**: You must maintain a `plan.md` or `PRD.md` file.
- **Rule**: Before writing any code, you must read the active plan.
- **Rule**: If you complete a step, you MUST check it off in `plan.md` using the `edit` tool immediately.

### ✅ Verification Protocol
After editing a file, you MUST:
1. **Syntactic Check**: Run the linter (`uv run ruff check .`) to ensure no syntax errors were introduced.
2. **Semantic Check**: Read the file again to verify indentation and logic flow.
3. **Test**: Run the relevant test immediately (`uv run pytest tests/path/to/test.py`). Do not wait for the user to ask.

### 🗺️ Codebase Map (for Agents)
- **Business Logic**: `services/*/app/services/` (Do not put business logic in API routes)
- **API Routes**: `services/*/app/api/` (Keep these thin)
- **Shared Utils**: `shared_commercial_libs/` (Check here before writing new utils)
- **Database Models**: `services/*/app/models/`
<!-- AI_INSTRUCTIONS_END -->

## Overview
This is the **root-level development guide** for the entire encypherai-commercial repository. All developers working on this codebase should read this file first.

---

## 🚨 CRITICAL: Documentation Maintenance

### When to Update Documentation

**ALWAYS update documentation when you:**
- ✅ Add a new component/service/tool
- ✅ Make breaking API changes
- ✅ Change architecture or dependencies
- ✅ Add/remove major features
- ✅ Modify configuration requirements
- ✅ Change development workflows

### Required Documentation Updates

When making major changes, you **MUST** update these files:

#### 1. Root Documentation (ALWAYS)
- **[README.md](./README.md)** - If adding new components or changing product tiers
- **[MICROSERVICES_FEATURES.md](./MICROSERVICES_FEATURES.md)** - If adding/modifying microservice features
- **[DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)** - Add new documentation files to index
- **[QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)** - If setup process changes

#### 2. Component Documentation (ALWAYS)
- **Component's README.md** - Usage, setup, API changes
- **Component's agents.md** - Development constraints, known issues

#### 3. Architecture Documentation (When Applicable)
- **[services/README.md](./services/README.md)** - If adding/modifying microservices
- **[docs/architecture/](./docs/architecture/)** - If changing system architecture
- **[DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md)** - Update audit findings if fixing issues

#### 4. Audit Documentation (Quarterly or After Major Changes)
- **[DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md)** - Re-audit after major changes
- **[AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md)** - Update completion status

### Documentation Update Checklist

```markdown
## Before Merging Your PR

- [ ] Updated component's README.md
- [ ] Updated component's agents.md (if constraints changed)
- [ ] Updated root README.md (if new component or tier change)
- [ ] Updated DOCUMENTATION_INDEX.md (if new docs added)
- [ ] Updated QUICK_START_GUIDE.md (if setup changed)
- [ ] Updated services/README.md (if microservice changes)
- [ ] Updated architecture docs (if architecture changed)
- [ ] Verified all links work
- [ ] Ran documentation linter (if available)
```

### Documentation Review Schedule

- **Weekly**: Check for outdated information in active components
- **Monthly**: Review all component READMEs for accuracy
- **Quarterly**: Full documentation audit (like October 2025 audit)
- **After Major Release**: Comprehensive documentation review

---

## 🎯 Development Principles

### 1. Package Management - UV ONLY

**CRITICAL**: This repository uses **UV exclusively** for Python package management.

```bash
# ✅ CORRECT - Use UV
uv add package-name
uv add --dev pytest
uv sync

# ❌ WRONG - Never use these
pip install package-name
poetry add package-name
# Never edit pyproject.toml directly to add packages
```

**Why UV?**
- Faster than pip/poetry
- Reproducible environments with uv.lock
- Consistent across all projects
- Better dependency resolution

### 2. Code Quality Standards

All code must meet these standards:

```bash
# Python projects
uv run ruff check .      # Linting
uv run black .           # Formatting
uv run mypy .            # Type checking
uv run pytest            # Tests

# JavaScript projects
npm run lint             # ESLint
npm run format           # Prettier
npm test                 # Tests
```

### 3. Testing Requirements

- **Minimum Coverage**: 80% for new code
- **Required Tests**: Unit, integration, e2e (where applicable)
- **Test Before Commit**: Always run tests before pushing
- **CI/CD**: All tests must pass in CI pipeline

### 4. Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/description

# 2. Make changes
# ... code changes ...

# 3. Run tests
uv run pytest  # or npm test

# 4. Commit with conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"

# 5. Push and create PR
git push origin feature/description
```

---

## 📁 Repository Structure

### Component Categories

#### CLI Tools (Free/Professional Tier)
- **[audit_log_cli/](./audit_log_cli/)** - Scan files, generate reports
  - ⚠️ Has known issues (see agents.md)
- **[policy_validator_cli/](./policy_validator_cli/)** - Policy validation
  - ✅ Production ready

#### Web Applications
- **[apps/marketing-site/](./apps/marketing-site/)** - encypherai.com
- **[apps/dashboard/](./apps/dashboard/)** - dashboard.encypherai.com
- **[dashboard_app/](./dashboard_app/)** - Enterprise compliance dashboard

#### Enterprise Products
- **[enterprise_api/](./enterprise_api/)** - C2PA API (Port 9000)
  - ✅ Production ready
- **[enterprise_sdk/](./enterprise_sdk/)** - Python SDK
  - ✅ Production ready

#### Microservices
- **[services/](./services/)** - Microservices architecture
  - **[auth-service/](./services/auth-service/)** - JWT/OAuth (Port 8001) ✅
  - **[key-service/](./services/key-service/)** - Key management (Port 8004) 🚧
  - 7 more planned services

#### Shared Libraries
- **[shared_commercial_libs/](./shared_commercial_libs/)** - Python shared library
- **[packages/design-system/](./packages/design-system/)** - React components

#### Integrations
- **[integrations/wordpress-assurance-plugin/](./integrations/wordpress-assurance-plugin/)** - WordPress plugin

---

## 🔧 Development Workflows

### Starting a New Component

1. **Create directory structure**
   ```bash
   mkdir new-component
   cd new-component
   ```

2. **Initialize project**
   ```bash
   # Python
   uv init
   uv add fastapi  # or other dependencies
   
   # JavaScript
   npm init
   npm install next react
   ```

3. **Create documentation**
   ```bash
   # Required files
   touch README.md
   touch agents.md
   touch .env.example
   ```

4. **Update root documentation**
   - Add to [README.md](./README.md) repository structure
   - Add to [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)
   - Add to [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) if user-facing

5. **Create tests**
   ```bash
   mkdir tests
   # Add test files
   ```

### Modifying Existing Component

1. **Read component documentation**
   - Component's README.md
   - Component's agents.md (known issues, constraints)

2. **Make changes**
   - Follow existing patterns
   - Maintain backward compatibility when possible

3. **Update tests**
   - Add tests for new functionality
   - Update existing tests if needed

4. **Update documentation**
   - Component's README.md
   - Component's agents.md (if constraints changed)
   - Root documentation (if major change)

5. **Run quality checks**
   ```bash
   uv run pytest --cov
   uv run ruff check .
   uv run black --check .
   ```

### Adding a New Microservice

1. **Follow microservices template**
   - See [services/README.md](./services/README.md)
   - Use auth-service as reference

2. **Required structure**
   ```
   service-name/
   ├── app/
   │   ├── main.py
   │   ├── api/v1/
   │   ├── core/
   │   ├── db/
   │   ├── models/
   │   └── services/
   ├── tests/
   ├── .env.example
   ├── Dockerfile
   ├── README.md
   ├── agents.md
   └── pyproject.toml
   ```

3. **Update documentation**
   - Add to [services/README.md](./services/README.md)
   - Update service diagram
   - Add to [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)

4. **Add to docker-compose**
   - Update [services/docker-compose.dev.yml](./services/docker-compose.dev.yml)

---

## 🚨 Known Issues

### Critical Issues (Fix Before Using)

#### audit_log_cli
**Location**: [audit_log_cli/](./audit_log_cli/)  
**Issues**:
1. Duplicate dependencies in pyproject.toml
2. Duplicate imports in app/main.py
3. Incomplete function definition

**Solution**: See [audit_log_cli/agents.md](./audit_log_cli/agents.md) for details

**Status**: ⚠️ Functional but needs refactoring

### No Other Critical Issues
All other components are production-ready.

---

## 🔐 Security Guidelines

### Secrets Management
- **Never commit secrets** to git
- Use `.env` files (gitignored)
- Provide `.env.example` templates
- Use environment variables in production

### API Keys
- Store in environment variables
- Rotate regularly (90 days)
- Use scoped keys when possible
- Hash keys in database

### Database Security
- Use parameterized queries (SQLAlchemy)
- Encrypt sensitive data at rest
- Use SSL/TLS connections
- Regular backups

### Authentication
- Use JWT with short expiration
- Implement refresh tokens
- Hash passwords with bcrypt
- Rate limit authentication endpoints

---

## 📊 Monitoring & Observability

### Health Checks
All services must expose `/health` endpoint:
```json
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0"
}
```

### Logging
- Use structured logging (JSON)
- Include correlation IDs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Never log sensitive data

### Metrics
- Expose Prometheus metrics at `/metrics`
- Track request counts, latency, errors
- Monitor resource usage
- Set up alerts for anomalies

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /____\
     /      \  Integration Tests (30%)
    /________\
   /          \  Unit Tests (60%)
  /__________\
```

### Testing Requirements

**Unit Tests**
- Test individual functions/classes
- Mock external dependencies
- Fast execution (<1s per test)
- 80%+ coverage

**Integration Tests**
- Test API endpoints
- Use test database
- Test service interactions
- 70%+ coverage

**End-to-End Tests**
- Test complete user flows
- Use Docker Compose for services
- Run before deployment
- Critical paths only

---

## 🚀 Deployment

### Environments

- **Development**: Local development
- **Staging**: Pre-production testing
- **Production**: Live environment

### Deployment Checklist

```markdown
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Monitoring configured
- [ ] Rollback plan prepared
- [ ] Team notified
```

### CI/CD Pipeline

1. **On Push**: Run tests, linting
2. **On PR**: Full test suite, coverage check
3. **On Merge to Main**: Deploy to staging
4. **On Tag**: Deploy to production

---

## 📚 Learning Resources

### For New Developers

**Week 1: Orientation**
1. Read [README.md](./README.md)
2. Read [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)
3. Set up development environment
4. Run a component locally

**Week 2: Deep Dive**
1. Read [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)
2. Read [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md)
3. Explore component agents.md files
4. Review architecture documentation

**Week 3: Contribution**
1. Pick a component to work on
2. Read component's README.md and agents.md
3. Make a small change
4. Submit your first PR

### Essential Documentation

**Must Read**:
- [README.md](./README.md) - Repository overview
- [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - Quick setup
- [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Navigation
- This file (agents.md) - Development guidelines

**Architecture**:
- [services/README.md](./services/README.md) - Microservices
- [docs/architecture/](./docs/architecture/) - System design
- [enterprise_api/README.md](./enterprise_api/README.md) - API reference

**Component Guides**:
- Each component's README.md - Usage
- Each component's agents.md - Development constraints

---

## 🤝 Contributing

### Code Review Guidelines

**Reviewers Should Check**:
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Backward compatibility maintained
- [ ] Performance impact considered

**Authors Should**:
- [ ] Self-review before requesting review
- [ ] Respond to feedback promptly
- [ ] Update based on comments
- [ ] Ensure CI passes
- [ ] Squash commits if needed

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] README.md updated
- [ ] agents.md updated (if needed)
- [ ] DOCUMENTATION_INDEX.md updated (if needed)
- [ ] API docs updated (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

## 🔗 Quick Links

### Documentation
- [README.md](./README.md) - Start here
- [MICROSERVICES_FEATURES.md](./MICROSERVICES_FEATURES.md) - Complete service feature matrix
- [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - 15-minute setup
- [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Complete index
- [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md) - Audit report
- [AUDIT_COMPLETE.md](./AUDIT_COMPLETE.md) - Quick summary

### Architecture
- [services/README.md](./services/README.md) - Microservices
- [enterprise_api/README.md](./enterprise_api/README.md) - API
- [docs/architecture/](./docs/architecture/) - System design

### Component Guides (agents.md)
- [audit_log_cli/agents.md](./audit_log_cli/agents.md)
- [policy_validator_cli/agents.md](./policy_validator_cli/agents.md)
- [enterprise_api/agents.md](./enterprise_api/agents.md)
- [services/auth-service/agents.md](./services/auth-service/agents.md)
- [shared_commercial_libs/agents.md](./shared_commercial_libs/agents.md)

---

## 📞 Support

### Internal Team
- **Slack**: #encypher-dev
- **Email**: dev-team@encypherai.com

### External
- **Enterprise**: enterprise@encypherai.com
- **API Issues**: api@encypherai.com
- **SDK Issues**: sdk@encypherai.com

---

## 📝 Version History

- **October 30, 2025**: Initial comprehensive documentation audit
  - Created 11 new documentation files
  - Documented microservices architecture
  - Established documentation standards
  - Repository health: 8.5/10

---

## ✅ Final Checklist for Developers

Before starting work:
- [ ] Read this file (agents.md)
- [ ] Read [README.md](./README.md)
- [ ] Read [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)
- [ ] Set up development environment
- [ ] Read component's README.md
- [ ] Read component's agents.md

Before committing:
- [ ] Run tests
- [ ] Run linting/formatting
- [ ] Update documentation
- [ ] Self-review changes

Before merging:
- [ ] All CI checks pass
- [ ] Documentation updated
- [ ] PR approved
- [ ] No merge conflicts

---

**Remember**: Good documentation is as important as good code. Keep it updated! 📚

**Last Updated**: October 30, 2025  
**Next Review**: January 30, 2026 (or after major changes)
