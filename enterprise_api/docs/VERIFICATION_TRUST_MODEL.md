# Verification Trust Model

## Scope

This document describes the trust and decision model for verification outcomes produced by Enterprise API verification endpoints.

It applies to both:
- `POST /api/v1/verify`
- `POST /api/v1/verify/advanced`

## Verification pipeline

### 1) Primary path (C2PA)

The **primary** verification path validates C2PA signature/manifest integrity using signer key resolution and trust checks.

High-level checks include:
- signature validity
- signer resolution
- certificate trust status
- revocation status assertion evaluation

### 2) Fallback path

If primary C2PA verification does not resolve a valid signer, verification may use **fallback** marker paths:
- `micro` marker fallback (VS256/VS256-RS)
- `legacy_safe` marker fallback (ZW6 base-6, Word-compatible)

For micro mode, verification uses sentence-level binding when available and legacy-compatible behavior for older markers.

## Micro fallback semantics

- Signatures are bound to sentence content in current mode.
- Verification computes sentence commitment and validates marker HMAC.
- Legacy UUID-only markers remain supported for backward compatibility.

## Trust status and reason_code

`reason_code` is the machine-readable SSOT for client logic.

Common outcomes:
- `OK`: valid and trusted verification outcome
- `SIGNATURE_INVALID`: signature/commitment mismatch
- `UNTRUSTED_SIGNER`: cryptographically valid but signer certificate chain not trusted
- `CERT_NOT_FOUND`: signer certificate unavailable
- `DOC_REVOKED`: document revoked via status list assertion

Related flags/details include:
- `untrusted_signer`
- `trust_status`
- revocation check details (including status list metadata)

## Revocation model

When present, `org.encypher.status` assertion values are used to evaluate revocation:
- status list URL
- bit index

If revoked, verification returns invalid with `reason_code=DOC_REVOKED`.

## Client guidance

- Use `reason_code` for deterministic branching.
- Treat `UNTRUSTED_SIGNER` as a policy decision (accept/reject) in your product tier.
- Preserve correlation IDs for auditability.
- For legal/compliance workflows, store full verification payloads and timestamps.
