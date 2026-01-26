# Enterprise API Key Management Readiness

**Status**: Drafted for production readiness review
**Scope**: API keys + signing keys (Ed25519/KMS)
**Owners**: Security + API Engineering

## 1. Overview
The Enterprise API relies on scoped API keys for authentication and per-organization Ed25519 signing keys for C2PA signing. Keys are stored in Postgres with encryption and optional AWS KMS integration.

## 2. Current Capabilities
### 2.1 API Key Lifecycle
- **Creation**: Keys created via `/api/v1/keys` and seeded via provisioning.
- **Listing**: `/api/v1/keys` returns masked key metadata.
- **Rotation**: `/api/v1/keys/{key_id}/rotate` creates a new key and revokes the old key.
- **Revocation**: `/api/v1/keys/{key_id}` marks keys inactive and sets `revoked_at`.
- **Scopes**: Stored as JSONB and enforced via dependencies (`sign`, `verify`, `lookup`, `read`, `admin`).

### 2.2 Key Storage
- **API Keys**: Stored as SHA-256 hashes with prefixes for display.
- **Signing Keys**: Encrypted with AES-GCM using `KEY_ENCRYPTION_KEY` + `ENCRYPTION_NONCE`.
- **KMS Support**: Organizations may store `kms_key_id` + `kms_region` and use AWS KMS signing via `AWSSigner`.

### 2.3 Auditability
- Key actions are recorded in audit logs (`api_key.created`, `api_key.revoked`, `api_key.rotated`).

## 3. Rotation & Revocation Policies
| Key Type | Rotation | Revocation | Notes |
| --- | --- | --- | --- |
| API keys | 90-day rotation target | Immediate via revoke endpoint | Requires customer operational discipline |
| Signing keys | Planned (KMS/managed key rotation) | Manual rotation via key regeneration | Key rotation affects verification paths |

## 4. Recovery Procedures
1. **API Key Compromise**
   - Revoke compromised key.
   - Rotate to a new key with the same scopes.
   - Review audit logs for unauthorized activity.
2. **Signing Key Compromise**
   - Rotate signing key (KMS or re-encrypt private key).
   - Reissue certificates if BYOK is used.
   - Publish revocation note and invalidate impacted proofs where required.

## 5. Readiness Gaps
- **Formal rotation enforcement**: Define automated rotation cadence and alerting.
- **Signing key rotation playbook**: Document customer-facing migration steps.
- **KMS integration documentation**: Provide deployment checklist for `kms_key_id` + regional requirements.
- **Key escrow & recovery**: Define secure backup/recovery for non-KMS keys.

## 6. Validation
- `uv run pytest enterprise_api/tests/test_keys_api.py`
- `uv run pytest enterprise_api/tests/test_admin.py`
- `uv run ruff check enterprise_api/app/routers/keys.py enterprise_api/app/utils/crypto_utils.py`

## 7. References
- `enterprise_api/app/routers/keys.py`
- `enterprise_api/app/utils/crypto_utils.py`
- `enterprise_api/app/routers/audit.py`
