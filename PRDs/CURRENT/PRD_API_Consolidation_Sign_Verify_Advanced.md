# PRD: API Consolidation - Sign/Verify Advanced Endpoints

**Status:** In Progress  
**Owner:** TEAM_066  
**Created:** 2026-01-15  
**Target Completion:** TBD

---

## Overview

Consolidate Merkle tree indexing, source attribution, and plagiarism detection capabilities into unified `/api/v1/sign/advanced` and `/api/v1/verify/advanced` endpoints. Hard-deprecate standalone Merkle endpoints to simplify the API surface and improve developer experience.

**Key Insight:** Users think in terms of "sign content" and "verify content"—not "build Merkle trees" and "run attribution queries." By consolidating related capabilities into the primary sign/verify endpoints, we reduce cognitive overhead and API round-trips.

---

## Objectives

1. **Simplify API Surface**
   - Reduce from 5 endpoints (`/sign`, `/sign/advanced`, `/merkle/encode`, `/merkle/attribute`, `/merkle/detect-plagiarism`) to 2 primary endpoints (`/sign/advanced`, `/verify/advanced`)
   - Make Merkle indexing an **option on signing**, not a separate workflow

2. **Improve Developer Experience**
   - Single call to sign + index content for attribution
   - Single call to verify + check plagiarism/attribution
   - Eliminate multi-step workflows for common use cases

3. **Align with Industry Patterns**
   - Follow Stripe/Cloudflare/DocuSign pattern of "primary action + optional enrichments"
   - Use boolean flags and array parameters for feature opt-in

4. **Maintain Power-User Flexibility**
   - Keep `/enterprise/merkle/encode` for batch indexing of existing content
   - Support multi-level Merkle tree construction in one call

---

## Current State Problems

### Problem 1: Fragmented Workflows
**Scenario:** User wants to sign content AND make it searchable for attribution.

**Current (Bad):**
```bash
# Step 1: Sign the content
POST /api/v1/sign/advanced
{ "text": "...", "segmentation_level": "sentence" }

# Step 2: Index it for attribution (duplicate work!)
POST /api/v1/enterprise/merkle/encode
{ "text": "...", "segmentation_levels": ["sentence"] }
```

**Proposed (Good):**
```bash
# One call does both
POST /api/v1/sign/advanced
{ 
  "text": "...", 
  "segmentation_levels": ["sentence"],
  "index_for_attribution": true  # default for paid tiers
}
```

### Problem 2: Verification Requires Multiple Calls
**Scenario:** User wants to verify content AND check if it's plagiarized.

**Current (Bad):**
```bash
# Step 1: Verify the signature
POST /api/v1/verify
{ "text": "..." }

# Step 2: Check plagiarism
POST /api/v1/enterprise/merkle/detect-plagiarism
{ "target_text": "..." }
```

**Proposed (Good):**
```bash
# One call does both
POST /api/v1/verify/advanced
{ 
  "text": "...",
  "detect_plagiarism": true,
  "include_heat_map": true
}
```

### Problem 3: Quota/Feature Gating Inconsistency
- `sign/advanced` doesn't enforce Merkle quotas even though it builds Merkle trees
- Merkle endpoints require `merkle_enabled` feature flag, but quota table says Professional+ gets Merkle
- Users confused about which tier gets what

---

## Proposed Solution

### 1. Enhanced `/api/v1/sign/advanced`

#### New Request Schema
```typescript
interface SignAdvancedRequest {
  // Existing fields
  text: string;
  document_id?: string;
  segmentation_level?: "document" | "sentence" | "paragraph" | "section";
  manifest_mode?: "standard" | "lightweight_uuid" | "hybrid";
  embedding_strategy?: "concentrated" | "distributed" | "distributed_redundant";
  // ... other existing fields ...
  
  // NEW: Multi-level Merkle indexing
  segmentation_levels?: string[];  // default: [segmentation_level]
  
  // NEW: Explicit indexing control
  index_for_attribution?: boolean;  // default: true for Professional+, false for Starter
  
  // NEW: Merkle metadata
  merkle_metadata?: Record<string, any>;  // stored with Merkle roots
}
```

#### Behavior Changes
1. **Multi-level Merkle trees**
   - If `segmentation_levels` provided, build Merkle trees at ALL specified levels
   - Example: `["sentence", "paragraph"]` builds both trees in parallel
   - Enables fine-grained + coarse-grained attribution in one call

2. **Automatic indexing for paid tiers**
   - Professional/Business/Enterprise: `index_for_attribution` defaults to `true`
   - Starter: defaults to `false` (no Merkle quota)
   - Users can explicitly opt-out with `index_for_attribution: false`

3. **Quota enforcement**
   - Enforce `QuotaType.MERKLE_ENCODING` when Merkle trees are built
   - Count = number of segmentation levels (e.g., 2 levels = 2 quota units)

4. **Response includes Merkle metadata**
   ```typescript
   interface SignAdvancedResponse {
     // Existing fields...
     
     // NEW: Multi-level Merkle info
     merkle_trees?: {
       [level: string]: {
         root_hash: string;
         total_leaves: number;
         tree_depth: number;
         indexed: boolean;  // whether stored for attribution
       }
     };
   }
   ```

#### Tier Gating
| Feature | Starter | Professional | Business | Enterprise |
|---------|---------|--------------|----------|------------|
| Basic signing (`segmentation_level: "document"`) | ✅ | ✅ | ✅ | ✅ |
| Single-level Merkle (`segmentation_level: "sentence"`) | ❌ | ✅ (5K/mo) | ✅ (10K/mo) | ✅ Unlimited |
| Multi-level Merkle (`segmentation_levels: ["sentence", "paragraph"]`) | ❌ | ✅ (5K/mo) | ✅ (10K/mo) | ✅ Unlimited |
| Attribution indexing (`index_for_attribution: true`) | ❌ | ✅ | ✅ | ✅ |

---

### 2. New `/api/v1/verify/advanced` Endpoint

#### Request Schema
```typescript
interface VerifyAdvancedRequest {
  // Existing verify fields
  text: string;
  document_id?: string;
  
  // NEW: Attribution options
  include_attribution?: boolean;  // Find source documents
  segmentation_level?: "sentence" | "paragraph" | "section";  // for attribution
  
  // NEW: Plagiarism detection options
  detect_plagiarism?: boolean;  // Run overlap analysis
  min_match_percentage?: number;  // default: 10.0
  include_heat_map?: boolean;  // default: false
  
  // NEW: Scope control
  search_scope?: "organization" | "public" | "all";  // default: "organization"
}
```

#### Response Schema
```typescript
interface VerifyAdvancedResponse {
  // Existing verify fields
  success: boolean;
  valid: boolean;
  manifest?: C2PAManifest;
  
  // NEW: Attribution results (if include_attribution: true)
  attribution?: {
    query_hash: string;
    matches_found: number;
    sources: Array<{
      document_id: string;
      organization_id: string;
      root_hash: string;
      segmentation_level: string;
      matched_hash: string;
      confidence: number;
    }>;
  };
  
  // NEW: Plagiarism results (if detect_plagiarism: true)
  plagiarism?: {
    report_id: string;
    total_segments: number;
    matched_segments: number;
    overall_match_percentage: number;
    source_documents: Array<{
      document_id: string;
      matched_segments: number;
      match_percentage: number;
      confidence_score: number;
    }>;
    heat_map?: {
      positions: Array<{
        index: number;
        matched: boolean;
        source_count: number;
      }>;
      total_segments: number;
      matched_segments: number;
      match_percentage: number;
    };
  };
}
```

#### Behavior
1. **Always verify C2PA manifest first**
   - Extract and validate signature
   - Return `valid: false` if verification fails

2. **Optional attribution lookup**
   - If `include_attribution: true`, hash segments and search Merkle index
   - Enforces `QuotaType.MERKLE_ATTRIBUTION` quota

3. **Optional plagiarism detection**
   - If `detect_plagiarism: true`, run full overlap analysis
   - Enforces `QuotaType.MERKLE_PLAGIARISM` quota
   - Can combine with `include_attribution` in one call

4. **Scope control**
   - `organization`: only search org's own documents
   - `public`: only search publicly-indexed documents
   - `all`: search both (Enterprise only)

#### Tier Gating
| Feature | Starter | Professional | Business | Enterprise |
|---------|---------|--------------|----------|------------|
| Basic verification | ✅ | ✅ | ✅ | ✅ |
| Attribution lookup (`include_attribution`) | ❌ | ✅ (10K/mo) | ✅ (50K/mo) | ✅ Unlimited |
| Plagiarism detection (`detect_plagiarism`) | ❌ | ❌ | ✅ (5K/mo) | ✅ Unlimited |
| Cross-org search (`search_scope: "all"`) | ❌ | ❌ | ❌ | ✅ |

---

### 3. Hard-Deprecate Standalone Merkle Endpoints

#### Endpoints to Deprecate
1. `POST /api/v1/enterprise/merkle/attribute` → Use `verify/advanced?include_attribution=true`
2. `POST /api/v1/enterprise/merkle/detect-plagiarism` → Use `verify/advanced?detect_plagiarism=true`

#### Keep (Power Users)
- `POST /api/v1/enterprise/merkle/encode` — For batch indexing existing content without re-signing

#### Migration Path (N/A - no users)
Since there are no existing API users, we can:
1. Remove deprecated endpoints immediately
2. Update OpenAPI spec to remove them
3. Update SDK generation to exclude them
4. Update marketing site pricing table

---

## Implementation Tasks

### 1. Backend Changes

#### 1.1 Update `sign/advanced` Endpoint
- [ ] 1.1.1 Add `segmentation_levels: string[]` param to `EncodeWithEmbeddingsRequest`
- [ ] 1.1.2 Add `index_for_attribution: bool` param (default based on tier)
- [ ] 1.1.3 Add `merkle_metadata: dict` param
- [ ] 1.1.4 Update `encode_document_with_embeddings` to build multi-level Merkle trees
- [ ] 1.1.5 Enforce `QuotaType.MERKLE_ENCODING` when Merkle trees built
- [ ] 1.1.6 Return `merkle_trees` dict in response with per-level metadata
- [ ] 1.1.7 Update tier gating to allow Professional+ for Merkle features

#### 1.2 Create `verify/advanced` Endpoint
- [ ] 1.2.1 Create `VerifyAdvancedRequest` schema in verification-service
- [ ] 1.2.2 Create `VerifyAdvancedResponse` schema with attribution/plagiarism fields
- [ ] 1.2.3 Implement `POST /api/v1/verify/advanced` endpoint
- [ ] 1.2.4 Add attribution lookup logic (call MerkleService.find_sources)
- [ ] 1.2.5 Add plagiarism detection logic (call MerkleService.generate_attribution_report)
- [ ] 1.2.6 Enforce `QuotaType.MERKLE_ATTRIBUTION` and `QuotaType.MERKLE_PLAGIARISM` quotas
- [ ] 1.2.7 Implement `search_scope` filtering (organization/public/all)
- [ ] 1.2.8 Add tier gating (Professional+ for attribution, Business+ for plagiarism)

#### 1.3 Hard-Deprecate Merkle Endpoints
- [ ] 1.3.1 Remove `POST /api/v1/enterprise/merkle/attribute` endpoint
- [ ] 1.3.2 Remove `POST /api/v1/enterprise/merkle/detect-plagiarism` endpoint
- [ ] 1.3.3 Keep `POST /api/v1/enterprise/merkle/encode` (power users)
- [ ] 1.3.4 Update `enterprise_api/app/main.py` to remove deprecated routes

#### 1.4 Fix Merkle Feature Gating Inconsistency
- [ ] 1.4.1 Update `require_merkle_feature` dependency to check Professional+ (not Business+)
- [ ] 1.4.2 Align `TIER_FEATURES` in `quota.py` with actual enforcement
- [ ] 1.4.3 Update error messages to say "Professional tier or higher"

### 2. Testing

#### 2.1 Sign/Advanced Tests
- [ ] 2.1.1 Test multi-level Merkle tree construction (`segmentation_levels: ["sentence", "paragraph"]`)
- [ ] 2.1.2 Test `index_for_attribution` defaults (true for Professional+, false for Starter)
- [ ] 2.1.3 Test `index_for_attribution: false` opt-out (no Merkle quota consumed)
- [ ] 2.1.4 Test Merkle quota enforcement (Professional tier with 5K/mo limit)
- [ ] 2.1.5 Test response includes `merkle_trees` dict with per-level metadata
- [ ] 2.1.6 Test tier gating (403 for Starter attempting Merkle features)

#### 2.2 Verify/Advanced Tests
- [ ] 2.2.1 Test basic verification (no attribution/plagiarism flags)
- [ ] 2.2.2 Test `include_attribution: true` returns source matches
- [ ] 2.2.3 Test `detect_plagiarism: true` returns plagiarism report with heat map
- [ ] 2.2.4 Test combined attribution + plagiarism in one call
- [ ] 2.2.5 Test `search_scope` filtering (organization/public/all)
- [ ] 2.2.6 Test quota enforcement for attribution and plagiarism
- [ ] 2.2.7 Test tier gating (Professional for attribution, Business for plagiarism)
- [ ] 2.2.8 Test Enterprise-only cross-org search

#### 2.3 Deprecation Tests
- [ ] 2.3.1 Verify `/enterprise/merkle/attribute` returns 404 or 410 Gone
- [ ] 2.3.2 Verify `/enterprise/merkle/detect-plagiarism` returns 404 or 410 Gone
- [ ] 2.3.3 Verify `/enterprise/merkle/encode` still works (not deprecated)

### 3. Documentation & SDK

#### 3.1 OpenAPI Spec
- [ ] 3.1.1 Add `POST /api/v1/verify/advanced` to verification-service OpenAPI
- [ ] 3.1.2 Update `POST /api/v1/sign/advanced` schema with new params
- [ ] 3.1.3 Remove deprecated Merkle endpoints from OpenAPI
- [ ] 3.1.4 Regenerate merged `sdk/openapi.public.json`
- [ ] 3.1.5 Verify OpenAPI contract tests pass

#### 3.2 SDK Generation
- [ ] 3.2.1 Regenerate Python SDK with new endpoints
- [ ] 3.2.2 Regenerate TypeScript SDK with new endpoints
- [ ] 3.2.3 Regenerate Go SDK with new endpoints
- [ ] 3.2.4 Regenerate Rust SDK with new endpoints
- [ ] 3.2.5 Bump SDK version to `2.0.0` (breaking change)

#### 3.3 README Updates
- [ ] 3.3.1 Update `enterprise_api/README.md` endpoint table
- [ ] 3.3.2 Update `services/verification-service/README.md` endpoint table
- [ ] 3.3.3 Add migration guide (even though no users, for future reference)
- [ ] 3.3.4 Update quickstart examples to use new consolidated endpoints

#### 3.4 Marketing Site
- [ ] 3.4.1 Update `FeatureComparisonTable.tsx` to reflect new endpoint structure
- [ ] 3.4.2 Remove references to deprecated Merkle endpoints
- [ ] 3.4.3 Add "Advanced Verification" row with attribution/plagiarism features
- [ ] 3.4.4 Update tier availability for Merkle features (Professional+, not Business+)

### 4. Deployment

#### 4.1 Database Migrations
- [ ] 4.1.1 No schema changes required (reusing existing Merkle tables)

#### 4.2 Service Deployment
- [ ] 4.2.1 Deploy updated `enterprise-api` with enhanced `sign/advanced`
- [ ] 4.2.2 Deploy updated `verification-service` with new `verify/advanced`
- [ ] 4.2.3 Update Traefik routing (if needed for new verify/advanced endpoint)

#### 4.3 Monitoring
- [ ] 4.3.1 Add metrics for `verify/advanced` attribution/plagiarism usage
- [ ] 4.3.2 Add metrics for multi-level Merkle tree construction
- [ ] 4.3.3 Monitor quota consumption patterns for new consolidated endpoints

---

## Success Criteria

1. **API Simplification**
   - ✅ Users can sign + index content in one call
   - ✅ Users can verify + check plagiarism in one call
   - ✅ Deprecated Merkle endpoints removed from OpenAPI

2. **Feature Parity**
   - ✅ All Merkle capabilities available via sign/verify endpoints
   - ✅ Multi-level Merkle tree construction supported
   - ✅ Attribution, plagiarism, heat maps all accessible

3. **Tier Gating Consistency**
   - ✅ Professional+ gets Merkle features (not Business+)
   - ✅ Quota enforcement matches tier availability
   - ✅ Error messages accurate for required tier

4. **Testing**
   - ✅ All unit tests pass
   - ✅ All integration tests pass
   - ✅ OpenAPI contract tests pass
   - ✅ SDK generation succeeds for all languages

5. **Documentation**
   - ✅ README endpoint tables updated
   - ✅ Marketing site pricing table accurate
   - ✅ Migration guide created (for reference)

---

## Open Questions

1. **Should `verify/advanced` be in verification-service or enterprise-api?**
   - Recommendation: verification-service (keeps verify logic consolidated)
   - Requires: verification-service needs access to Merkle DB tables

2. **Should we version the API to `/api/v2/` for this breaking change?**
   - Recommendation: No, since there are no existing users
   - Keep `/api/v1/` and just update endpoints

3. **Should `index_for_attribution` default be tier-based or always explicit?**
   - Recommendation: Tier-based default (true for Professional+, false for Starter)
   - Rationale: Most paid users want indexing; explicit opt-out available

4. **Should we keep `/enterprise/merkle/encode` or deprecate it too?**
   - Recommendation: Keep it for batch indexing existing content
   - Use case: User has 10K documents already signed, wants to index them all

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Verification-service needs Merkle DB access | High | Share Merkle DB connection or create read-only replica |
| Multi-level Merkle increases latency | Medium | Run tree construction in parallel; add timeout limits |
| Quota enforcement complexity | Medium | Reuse existing QuotaManager; add comprehensive tests |
| Marketing site out of sync with API | Low | Update pricing table as part of this PRD |

---

## Completion Notes

_(To be filled in after implementation)_

- Final implementation date:
- Actual duration:
- Deviations from plan:
- Lessons learned:
