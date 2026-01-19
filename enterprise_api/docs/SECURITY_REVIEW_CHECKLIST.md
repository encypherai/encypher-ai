# Enterprise API Security Review Checklist

**Status**: Drafted for production readiness review
**Scope**: SOC2/GDPR alignment, pen-test scope, and operational hardening
**Owners**: Security + Compliance + API Engineering

## 1. Governance & Compliance
- [ ] Confirm SOC2 Type II control mapping for Enterprise API (access control, logging, change management).
- [ ] Confirm GDPR data processing inventory for API endpoints.
- [ ] Verify data processing agreements and subprocessors list.
- [ ] Validate privacy policy alignment with retention schedule.

## 2. Authentication & Authorization
- [ ] Key Service validation required for all authenticated endpoints.
- [ ] Demo key allowlist enforced in production.
- [ ] Scoped permissions enforced for sign/verify/lookup/admin.
- [ ] Super admin access requires `admin` scope or feature flag.

## 3. Cryptography & Key Management
- [ ] API keys hashed at rest (SHA-256) with prefix masking.
- [ ] Signing keys encrypted with AES-GCM or stored in KMS.
- [ ] Key rotation + revocation endpoints operational.
- [ ] Trust list pinning + refresh enforced for C2PA validation.

## 4. Data Protection & Privacy
- [ ] PII minimization in logs (no content payloads in public verify flows).
- [ ] Retention windows implemented (audit logs 2 years, deletions 90 days, verification 7 years).
- [ ] Deletion request workflow documented and enforced.
- [ ] Encryption in transit (TLS 1.2+) and at rest (AES-256).

## 5. Network & Transport Protections
- [ ] TrustedHost middleware enabled in production.
- [ ] CORS restricted to allowed origins.
- [ ] Security headers (HSTS, CSP, XFO, Referrer-Policy) enabled.
- [ ] Rate limiting enforced for public endpoints with trusted proxy allowlist.

## 6. Monitoring & Incident Response
- [ ] Structured logging with correlation IDs.
- [ ] Security alerts and audit log monitoring in place.
- [ ] Incident response runbook documented.
- [ ] On-call escalation procedures defined.

## 7. Pen-Test Scope
- [ ] Public verification endpoints (enumeration, signature bypass).
- [ ] API key auth + scope enforcement.
- [ ] Admin endpoints for privilege escalation.
- [ ] Key rotation + revocation flows.
- [ ] C2PA trust list fetcher and pinning logic.
- [ ] Injection vectors (SQL, XSS, SSRF) across API inputs.

## 8. Evidence & Validation
- [ ] `uv run pytest` baseline passes.
- [ ] Security regression tests documented.
- [ ] Dependency audit (pip-audit via uv) complete.
- [ ] Pen-test report attached to readiness review.
