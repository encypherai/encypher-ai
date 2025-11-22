# WordPress Provenance Plugin - Tier Audit

**Date:** November 21, 2025
**Auditor:** Cascade

## Production Readiness Status
✅ **Production Ready**

The plugin implements all core requirements for C2PA content authentication and is fully integrated with the Encypher Enterprise API.

---

## Tier Definitions & Implementation

The plugin codebase (`encypher-provenance`) implements distinct features for Free, Pro, and Enterprise tiers, enforced via both UI logic and backend API parameters.

### 1. Free Tier
*   **Target:** Individual bloggers, small sites.
*   **Signature:** Shared Encypher-managed key (`signing_mode = 'managed'`).
*   **Granularity:** Document-level only (1 C2PA manifest per post).
    *   *Implementation:* `class-encypher-provenance-rest.php` forces `'segmentation_level' => 'document'`.
*   **Bulk Marking:** Limited to 100 posts per batch.
    *   *Implementation:* `class-encypher-provenance-bulk.php` checks count limit.
*   **Coalition:** Mandatory participation.
    *   *Implementation:* `class-encypher-provenance-admin.php` forces `coalition_enabled = true`.

### 2. Pro Tier ($99/mo)
*   **Target:** Professional publishers, newsrooms.
*   **Signature:** Custom Signing Profile (BYOK support).
    *   *Implementation:* Settings UI allows `signing_mode = 'byok'` and `signing_profile_id` input.
*   **Granularity:** Sentence-level tracking (Merkle tree).
    *   *Implementation:* API payload uses `'segmentation_level' => 'sentence'`.
*   **Bulk Marking:** Unlimited.
*   **Coalition:** Optional.

### 3. Enterprise Tier
*   **Target:** Large media conglomerates, agencies.
*   **Features:** Inherits all Pro features (BYOK, Sentence-level).
*   **Differentiation:** Handled primarily via the **Enterprise API Backend**:
    *   Higher rate limits.
    *   HSM-backed signing profiles (configured in Encypher Dashboard).
    *   SLA & Dedicated Support.
*   **Plugin Logic:** Treats 'enterprise' same as 'pro' for feature flags (unlocks all capabilities).

---

## Microservices Integration

The plugin correctly utilizes the Enterprise microservices architecture:

*   **Authentication:** Uses `Authorization: Bearer {api_key}` for all requests.
*   **Embeddings Service:** Calls `POST /enterprise/embeddings/encode-with-embeddings` for signing.
    *   Sends `segmentation_level` to trigger appropriate microservice workflow (Merkle vs Simple).
    *   Preserves provenance chain via `previous_instance_id` and `action` (`c2pa.created` vs `c2pa.edited`).
*   **Verification Service:** Calls `POST /public/extract-and-verify` for frontend badges.
    *   Displays Merkle proof data if available.

## Recommendations
*   **Update README:** Clarify the features available per tier in the public documentation.
*   **Docker Port:** Ensure local development instructions match `docker-compose.yml` (Port 8001).
