# Enterprise API Threat Model

**Status**: Drafted for production readiness review
**Scope**: Enterprise archive workflows (ingestion/signing, verification, public proofs)
**Owners**: Security + API Engineering

## 1. System Overview
The Enterprise API ingests customer content, signs it with C2PA-compatible manifests, persists metadata and proofs, and exposes verification endpoints (including public verification flows). It depends on:
- PostgreSQL (core data store for content references, audit logs, keys)
- Redis (caching/session/metrics)
- Key Service (API key validation + org context)
- Optional KMS (AWS) for signing key storage
- C2PA Trust List fetcher (BYOK certificate validation)

## 2. Assets
| Asset | Description | Sensitivity |
| --- | --- | --- |
| Signing private keys | Ed25519 keys per org, optionally in KMS | Critical |
| API keys + scopes | Key-based auth for all endpoints | High |
| C2PA manifests + proofs | Verification data for content | High |
| Content metadata | Titles, URLs, segments, signatures | High |
| Audit logs | Security/compliance activity trail | Medium |
| Public verification data | Limited metadata for public proofs | Medium |

## 3. Trust Boundaries
1. **Client → Enterprise API** (public internet, auth boundaries)
2. **Enterprise API → Database** (internal network)
3. **Enterprise API → Key Service** (service-to-service auth)
4. **Enterprise API → KMS/Key storage** (credential boundary)
5. **Enterprise API → C2PA Trust List source** (external dependency)

## 4. Data Flows
### 4.1 Ingestion/Signing
1. Client submits content to `/api/v1/sign` or `/api/v1/sign/advanced`.
2. API validates API key + scopes, loads org signing key.
3. Service generates C2PA manifest, stores content reference + proof.
4. Audit events captured for key/sign operations.

### 4.2 Verification
1. Client submits content to `/api/v1/verify` or `/api/v1/verify/advanced`.
2. API validates API key + scopes (or public auth for limited endpoints).
3. Service validates signatures + manifests, returns verification response.

### 4.3 Public Proofs
1. Anonymous users access `/api/v1/public/verify` endpoints.
2. API rate limits by IP + signature validation to prevent enumeration.
3. Limited metadata disclosed; no private data.

## 5. Threats and Mitigations (STRIDE)
### Spoofing
- **Threat**: API key theft → unauthorized access.
  - **Mitigation**: Scoped keys, demo-key gating in production, revocation and rotation endpoints.
- **Threat**: Forged C2PA trust list.
  - **Mitigation**: SHA-256 trust list pinning and refresh policy.

### Tampering
- **Threat**: Modify manifests or content references in transit.
  - **Mitigation**: TLS, cryptographic signatures, DB integrity constraints.
- **Threat**: Tamper with audit logs.
  - **Mitigation**: Append-only audit log pattern, least-privilege DB access.

### Repudiation
- **Threat**: Actions cannot be traced to an actor.
  - **Mitigation**: Audit logs capture actor, action, IP/user agent.

### Information Disclosure
- **Threat**: Public verify endpoints leak metadata.
  - **Mitigation**: Signature validation against stored hash, strict response schema.
- **Threat**: Sensitive logs.
  - **Mitigation**: Logging policy to avoid content payloads in public flows.

### Denial of Service
- **Threat**: Abuse public endpoints with spoofed IPs.
  - **Mitigation**: Trusted proxy allowlist for forwarded headers, IP rate limiting.

### Elevation of Privilege
- **Threat**: Non-admin calls admin endpoints.
  - **Mitigation**: `admin` scope + `is_super_admin` feature flag enforcement.

## 6. Residual Risks / Open Items
- Formalized pen-test scope with third-party security assessment.
- Automated log redaction policy across all public endpoints.
- Documented disaster recovery procedures for key compromise.

## 7. Validation
- Security regression tests in `enterprise_api/tests/*`.
- `uv run pytest` for baseline regression.
- Manual verification for public proof flows.

## 8. References
- `enterprise_api/app/middleware/api_key_auth.py`
- `enterprise_api/app/dependencies.py`
- `enterprise_api/app/utils/c2pa_trust_list.py`
- `enterprise_api/app/middleware/public_rate_limiter.py`
- `enterprise_api/app/routers/audit.py`
