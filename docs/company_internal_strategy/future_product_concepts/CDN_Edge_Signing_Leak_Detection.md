# CDN Edge Signing & Distribution Leak Detection

**Created:** March 22, 2026
**Status:** Concept / Pre-Development
**Owner:** Product + Engineering
**Distribution:** Executive, Product, Engineering, BD, Legal

---

## Concept Summary

Partner with CDNs (Cloudflare, Fastly, Akamai) or ad-tech delivery platforms to sign content on demand at the delivery edge, embedding per-session/per-subscriber context into the content via invisible fingerprinting. When content leaks (scraped, redistributed, fed to AI training), the publisher can trace the leak back to the exact user session, subscriber account, referral path, and timestamp.

This extends our existing Enterprise-tier fingerprint service from a single-document tool into a distribution-layer forensic infrastructure.

---

## Strategic Rationale

### From "What Leaked" to "Who Leaked It"

Today, Tier 1 detection (Attribution Analytics / Chrome extension) answers: "My article appeared on site X."

With per-session edge fingerprinting, the same detection answers: "My article appeared on site X, and it was leaked from subscriber account Y who accessed it at timestamp Z from referrer W."

This is forensic-grade leak detection -- dramatically more valuable for publishers with paywalled content.

### New Buyer, New Budget

Current ICP targets: Editorial, Legal, Communications, CTO.
This capability targets: **Head of Subscriptions / VP Revenue** -- protecting paywall investment.

Positions Encypher as **paywall enforcement infrastructure**, not just compliance tooling. Different buyer, different (often larger) budget line.

### Competitive Separation

No competitor can match this because it requires both:
1. Patent-pending sentence-level embedding tech (ENC0100)
2. Delivery-layer integration partnerships

| Competitor | Can They Do This? |
|---|---|
| TollBit / Cloudflare AI Audit | No -- opt-in access gates, no forensic attribution |
| ProRata / Dappier | No -- opt-in attribution, no unilateral leak tracing |
| Digimarc | No -- image/video only, no text |
| CDNs (build-your-own) | Partial -- can do document-level signing, cannot do sentence-level Merkle trees or verification infrastructure |

---

## Technical Architecture

### Delivery Flow

```
Publisher CMS --> CDN Edge (Workers / Compute@Edge / Lambda@Edge)
                     |
                     |-- (1) Content arrives pre-signed at document level (C2PA)
                     |-- (2) Edge worker extracts session context:
                     |       subscriber_id, session_id, referrer, geo, timestamp
                     |-- (3) Edge applies fingerprint layer (HMAC PRNG markers)
                     |       using session-derived key
                     |-- (4) Fingerprinted content delivered to end user
                     |-- (5) Session metadata posted to Encypher async
```

### Two-Phase Signing (Critical Design Decision)

- **Phase 1 (publish time):** Full C2PA signing with Merkle trees -- document-level provenance. Cached at CDN normally.
- **Phase 2 (delivery time):** Lightweight fingerprint-only layer applied at edge. Orthogonal to C2PA manifest -- does not invalidate document-level hash.

This preserves CDN caching for the base content. Only the fingerprint computation runs per-request, which is pure HMAC + string insertion -- no origin hit required.

### Hierarchical Key Derivation

```
master_key (per publisher org)
  --> doc_key = HMAC(master_key, document_id)
    --> session_key = HMAC(doc_key, session_id || subscriber_id || timestamp)
```

Keys are deterministically derived, not stored. Only session metadata tuples need persistent storage. During detection, candidate session keys are re-derived from metadata.

### Relationship to Existing Architecture

| Component | Current State | Edge Signing Extension |
|---|---|---|
| `fingerprint_service.py` | Enterprise-tier, HMAC PRNG, in-memory storage | Hierarchical key derivation, persistent storage, session metadata index |
| `SignOptions.include_fingerprint` | Boolean flag in signing endpoint | Fingerprint-only endpoint (no C2PA re-signing) |
| `SignOptions.add_dual_binding` | C2PA + fingerprint in one pass | Pre-signed C2PA + edge-applied fingerprint (two-phase) |
| Detection tiers | Tier 1 = web-surface detection | Tier 1 + forensic session attribution |

### Target Architecture: Edge WASM SDK

The highest-value technical artifact is a WASM module that runs the HMAC PRNG + marker insertion algorithm inside the CDN worker:

- Accepts a derived document key (fetched once per article from Encypher API, cached at edge)
- Generates session key locally from session context
- Inserts markers with zero API call latency
- POSTs session metadata to Encypher asynchronously (fire-and-forget)

This delivers "provenance at CDN speed with zero latency impact."

---

## Key Technical Challenges

### 1. CDN Cache Invalidation

Per-session fingerprinting converts cacheable content into unique-per-response content. Mitigation: cache base content, apply fingerprint computation at edge only (WASM SDK approach). No origin hit required.

### 2. Fingerprint Detection at Scale

A popular article with 1M page views generates 1M session records. Detection of leaked content requires matching against candidate keys. Mitigations:
- Hierarchical key derivation (re-derive, don't store keys)
- Time-window partitioning to narrow search
- Marker pattern as bloom-filter-style pre-filter
- Consider direct session ID encoding in fingerprint pattern for O(1) extraction

### 3. Signing Key Distribution

Edge workers need derived document keys. This is a key management problem -- trusting the CDN's security boundary. Mitigations: Cloudflare Workers Secrets / KV, ephemeral scoped certificates, short rotation periods.

### 4. Ad-Tech Wrapper Limitations

Prebid wrappers and header bidding solutions operate in the ad slot, not the content body. They cannot modify article text without publisher-side DOM manipulation. **Recommendation:** CDN-level signing is the clean technical path. Ad-tech partners are valuable as distribution/sales channels, not as the signing mechanism.

---

## New API Surface Required

### 1. Lightweight Fingerprint-Only Endpoint

```
POST /api/v1/enterprise/fingerprint/embed
{
  "text": "...",
  "document_id": "article-12345",
  "session_context": {
    "session_id": "sess_abc",
    "subscriber_id": "sub_xyz",
    "referrer": "https://news.ycombinator.com/...",
    "geo": "US-CA",
    "timestamp": "2026-03-21T10:00:00Z"
  },
  "density": 0.05
}
```

Response: fingerprinted text + fingerprint_id. No C2PA re-signing. Sub-10ms target.

### 2. Leak Source Identification Endpoint

```
POST /api/v1/enterprise/fingerprint/identify
{
  "text": "...(leaked content)...",
  "document_id": "article-12345",
  "time_window": {
    "start": "2026-03-20T00:00:00Z",
    "end": "2026-03-21T23:59:59Z"
  }
}
```

Response: matched session context (subscriber, referrer, geo, timestamp) + confidence score.

### 3. Edge WASM SDK

Lightweight module for CDN workers. Zero-latency path -- no API call per request.

---

## Privacy & Legal Framework (Required Before Any Pilot)

### Privacy Architecture Rules

1. **Pseudonymous session tokens only** -- never embed raw PII (emails, names, subscriber IDs). Opaque session hash only. Mapping table held by publisher, not Encypher.
2. **Mandatory disclosure** -- publisher ToS must state content is individually watermarked for IP protection. Undisclosed watermarking risks "covert surveillance" characterization by regulators.
3. **90-day default retention** for session-to-user mappings.
4. **API-level enforcement** -- reject payloads containing PII-shaped values.

### GDPR Compliance

- Processing requires lawful basis (legitimate interest strongest -- publisher IP protection)
- Mandatory DPIA (Data Protection Impact Assessment)
- Transparency obligation under Art. 13/14
- Data minimization: pseudonymous tokens only

### CCPA/CPRA

- Right-to-know and right-to-delete create tension with leak detection
- Security/fraud exceptions may apply
- Must disclose in privacy policy

### Deliverables Before Pilot

- [ ] DPIA template for publisher partners
- [ ] Disclosure language for publisher ToS
- [ ] DPA addendum for CDN/ad-tech partners
- [ ] API-level PII rejection logic

---

## IP Protection (P0 Action)

### ENC0100 Coverage Analysis

**Covered (strong foundation):**
- Claims 56-60: Distributed embedding with pseudorandom carrier sequencing and key-derived positioning
- Claims 61-63: Multi-layer authentication (segment-level markers + document-level manifest)
- Spec [0101]: Explicitly mentions "session ID" as an embedding use case
- Claims 46-52: Streaming/real-time processing (applicable to edge signing)
- Claims 72-77: Fingerprinting with LSH for leak detection

**Not explicitly claimed (gaps):**
- Per-user/per-session dynamic re-signing of the same base content
- Edge/intermediary signing architecture (delegated signing)
- Dynamic content individualization at serving time
- Session/user binding with leak traceability method

### Recommended Action: File Continuation-in-Part (CIP)

Specification disclosure at [0101] (session ID mention) and distributed embedding disclosures provide a reasonable basis for new claims covering:
- Dynamic per-session/per-user signed content at a content delivery intermediary
- Key derivation incorporating user/session identifiers for per-recipient watermark individualization
- Leak traceability methods from embedded session identifiers to content recipients
- Delegated signing architectures where edge nodes sign on behalf of content owners

**Timeline: Engage patent counsel within 2 weeks of concept approval.**

---

## Partnership Strategy

### Recommended Partner Sequencing

| Phase | Partner | Rationale | Timeline |
|---|---|---|---|
| **1. Seed** | Freestar/PubOS | Already in legal review. Mention edge-signing as Phase 2 capability. Don't derail current close. | Now |
| **2. Ad-tech bridge** | Aditude | Prebid.org AI working group access. Intelligence-rich relationship. Rev-share aligned. | Q2 2026 |
| **3. First CDN** | Fastly | Strong media vertical, least competitive overlap, won't build their own | Q2-Q3 2026 |
| **4. Scale CDN** | Cloudflare | Highest value but most competitive risk. Approach after reference implementation exists. | Q3-Q4 2026 |

### Why Fastly Before Cloudflare

Cloudflare already has AI Audit tooling, bot management, and Workers -- they could build an inferior version themselves. Fastly is more infrastructure-focused, has a dedicated media vertical team, and is a partnership-first company. A working Fastly integration creates leverage that makes Cloudflare more likely to integrate than compete.

### Deal Structure

This creates a **third economic model** separate from 60/40 coalition and 80/20 self-service:
- **Pricing:** Enterprise add-on at $1,500-3,000/mo per publisher domain
- **CDN partner split:** 70/30 (Encypher/CDN) on SaaS subscription, or flat per-request fee ($0.001-0.005 per signing operation)
- **60/40 and 80/20 remain untouched** for licensing revenue

---

## Product Tier Fit

| Capability | Tier |
|---|---|
| Document-level C2PA signing (pre-publish) | Free |
| Fingerprint embedding (per-session) | Enterprise |
| Dual binding (C2PA + fingerprint) | Enterprise |
| Leak source identification | Enterprise (Enforcement add-on) |
| Edge WASM SDK | Enterprise |

Product name candidates: "Distribution Leak Detection" or "Session Provenance" (to distinguish from "Print Leak Detection" which covers print-to-scan pipelines).

---

## Priority Actions

| Priority | Action | Owner | Timeline |
|---|---|---|---|
| **P0** | Engage patent counsel on CIP for per-session dynamic embedding claims | Legal | 2 weeks |
| **P0** | Draft privacy architecture guidelines (pseudonymous-only, no raw PII) | Legal + Engineering | Before any pilot |
| **P1** | Create DPIA template for publisher partners | Legal | Q2 2026 |
| **P1** | Build lightweight fingerprint-only endpoint + identification endpoint | Engineering | Q2 2026 |
| **P1** | Draft CDN partnership term sheet | Legal + BD | Q2 2026 |
| **P2** | Develop edge WASM SDK prototype | Engineering | Q2-Q3 2026 |
| **P2** | Propose "individualized distribution" extension in C2PA task force | Product + Standards | Q3 2026 |
| **P3** | Approach Fastly for CDN partnership | BD | Q2-Q3 2026 |

---

## Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| Privacy backlash (undisclosed watermarking) | High | Mandatory disclosure in publisher ToS, pseudonymous tokens only, DPIA |
| CDN builds competing feature (Cloudflare) | Medium | Patent CIP, Fastly-first strategy, position as engine-inside-CDN |
| Scope creep dilutes core coalition motion | Medium | Strict Q2/Q3 timeline, don't displace current pipeline priorities |
| Fingerprint detection at scale (millions of sessions) | Medium | Hierarchical key derivation, time-window partitioning, O(1) extraction |
| Wrongful leak accusation liability | Medium | Position evidence as "investigative lead" not "proof," confidence scores, contractual indemnification |

---

## Success Criteria

- [ ] CIP filed with per-session dynamic embedding claims
- [ ] Privacy framework complete (DPIA template, disclosure language, DPA addendum)
- [ ] Fingerprint-only endpoint live with sub-10ms latency
- [ ] Single publisher pilot demonstrating session-to-leak attribution
- [ ] First CDN partnership signed (target: Fastly)
- [ ] C2PA task force briefed on individualized distribution use case
