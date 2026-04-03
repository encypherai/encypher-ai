# Enterprise API Privacy & Retention Policy (Engineering)

**Status**: Drafted for production readiness review
**Scope**: Enterprise API data handling (PII, content, audit logs)
**Owners**: Security + Legal + API Engineering

## 1. Purpose
This document translates the company privacy policy into engineering retention and deletion requirements for the Enterprise API.

## 2. Data Categories
| Category | Examples | Storage | Sensitivity |
| --- | --- | --- | --- |
| Account data | Org name, contact email, billing metadata | Postgres | High |
| Content metadata | Document IDs, URLs, signatures, manifests | Postgres | High |
| Verification records | Proofs, manifests, verification results | Postgres | High |
| Audit logs | Actor, action, IP, timestamp | Postgres | Medium |
| API usage logs | Endpoint, latency, status | Metrics/logging | Medium |

## 3. Retention Schedule (Aligned to Privacy Policy)
Source of truth: `docs/legal/PRIVACY_POLICY.md` (Sections 5 and 7).

### 3.1 Active Accounts
- Account information: retained until account deletion.
- Content metadata: retained indefinitely (required for verification proofs).
- API usage logs: retained for 2 years.
- Audit logs: retained for 2 years.

### 3.2 Deleted Accounts
- Account information: deleted after 90 days.
- Private data: deleted after 90 days.
- Verification records: retained for 7 years (legal compliance).
- Public verification data: retained indefinitely (independent verification requirements).

### 3.3 Legal Holds
- Data may be retained longer if required by law or during litigation holds.

## 4. Deletion & Access Requests
- Requests are handled via privacy@encypher.com (see Privacy Policy).
- Engineering must support:
  - Account deletion initiation with a 90-day purge window.
  - Audit log retention enforcement for 2 years.
  - Verification record retention for 7 years.

## 5. Engineering Requirements
1. **Soft-delete windows**: All account deletions must record request date + scheduled purge date.
2. **Retention enforcement**: Scheduled jobs required to purge account data beyond 90 days.
3. **Verification proof preservation**: Keep public verification artifacts indefinitely.
4. **Audit log retention**: Archive or prune logs older than 2 years.
5. **PII minimization**: Avoid logging content or user PII in public verification flows.

## 6. Open Gaps (Production Readiness)
- Implement automated purge jobs for 90-day deletion windows.
- Document audit log archival process (immutable storage or cold archive).
- Confirm privacy review sign-off with legal for retention schedule.

## 7. References
- `docs/legal/PRIVACY_POLICY.md`
- `enterprise_api/app/routers/audit.py`
- `enterprise_api/app/services/provisioning_service.py`
