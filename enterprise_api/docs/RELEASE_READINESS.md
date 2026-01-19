# Enterprise API Release Readiness

**Status**: Drafted for production readiness review
**Scope**: Staging parity, CI/CD gates, support onboarding
**Owners**: Platform + SRE + Support

## 1. Staging Parity Checklist (PRD 7.1)
- [ ] Staging mirrors production infrastructure (DB version, Redis, Key Service).
- [ ] Environment variables aligned with production (minus secrets).
- [ ] C2PA trust list pinning enabled.
- [ ] Trusted host and CORS configuration validated.
- [ ] SSL/TLS certificates configured and rotated.

## 2. CI/CD Gates (PRD 7.2)
- [ ] Linting: `uv run ruff check .`
- [ ] Type checks: `uv run mypy .`
- [ ] Tests: `uv run pytest`
- [ ] Security audit: `uv run pip-audit`
- [ ] Load tests: opt-in for release candidates.

## 3. Support Onboarding (PRD 7.3)
- [ ] SLA documentation with response targets.
- [ ] Escalation paths for security incidents.
- [ ] Customer runbooks for key rotation and recovery.
- [ ] Support contact matrix and on-call schedule.

## 4. Release Evidence
- Deployment checklist completed.
- Rollback plan documented.
- Post-deploy monitoring validated.

## 5. References
- `enterprise_api/docs/DEPLOYMENT.md`
- `enterprise_api/docs/TESTING_GUIDE.md`
