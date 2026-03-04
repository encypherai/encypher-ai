# Enterprise API Data Integrity & Auditability

**Status**: Drafted for production readiness review
**Scope**: Audit logs, consistency checks, proof export
**Owners**: Platform + API Engineering

## 1. Overview
Data integrity ensures signed content proofs, manifests, and audit trails remain tamper-evident and verifiable over time.

## 2. Immutable Audit Logs (PRD 5.1)
### Current State
- Audit logs stored in Postgres via `audit_logs` table.
- Audit log API supports export and filtering.
- The following events are written automatically by the signing and verification flows (asynchronous, best-effort):

  | Event constant | Event name | Emitted by |
  |----------------|------------|------------|
  | `DOCUMENT_SIGNED` | `document.signed` | Single-document signing endpoint |
  | `BATCH_SIGN_COMPLETED` | `batch.sign.started` | Batch signing endpoint on completion |
  | `DOCUMENT_VERIFIED` | `document.verified` | Document verification endpoint |

### Target State
- Append-only log storage and immutable archive (WORM storage or immutable S3 bucket).
- Signed audit log exports for compliance evidence.

### Open Gaps
- Implement immutable storage backend and retention policy enforcement.

## 3. Consistency Checks (PRD 5.2)
### Current State
- C2PA verification validates manifests and certificate chains.
- Merkle content references stored with hash links.

### Target State
- Periodic consistency job to validate manifest ↔ Merkle ↔ DB references.
- Detection of orphaned records or mismatched hashes.

### Open Gaps
- Background job to reconcile manifest UUIDs and content references.

## 4. Proof Export Tooling (PRD 5.3)
### Current State
- Verification endpoints return C2PA manifests and metadata.

### Target State
- Dedicated export endpoint for Merkle proofs and C2PA manifests.
- Archive-friendly evidence packages (JSON + manifest + chain).

### Open Gaps
- Define export package schema and retention for public proof downloads.

## 5. References
- `enterprise_api/app/routers/audit.py`
- `enterprise_api/app/services/verification_logic.py`
- `enterprise_api/app/utils/c2pa_trust_list.py`
