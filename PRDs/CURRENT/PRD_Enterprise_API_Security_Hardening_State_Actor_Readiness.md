# PRD: Enterprise API Security Hardening & State-Actor Readiness

## Status: IN_PROGRESS
## Current Goal: Complete the remaining observability, degraded-mode, rollout, and higher-scale validation controls after the verified Railway-feasible distributed abuse-control tranche.
## Related Docs: `enterprise_api/app/main.py`, `enterprise_api/app/dependencies.py`, `enterprise_api/app/api/v1/public/verify.py`, `enterprise_api/app/api/v1/image_verify.py`, `enterprise_api/app/routers/webhooks.py`, `enterprise_api/app/services/webhook_dispatcher.py`, `enterprise_api/app/utils/c2pa_verifier.py`, `PRDs/ARCHIVE/enterprise_api_launch_audit.md`

---

## Overview

The Enterprise API is already structured with clear FastAPI routing, typed request models, host filtering, basic security headers, and some public-endpoint protections. However, the current implementation still contains several exploitable gaps that become serious under a determined, well-resourced adversary model.

This PRD defines the work needed to harden `enterprise_api` against:

- credential theft and replay
- globally distributed botnet traffic
- public endpoint resource exhaustion
- webhook spoofing and outbound abuse
- trust-confusion attacks in verification flows
- service-to-service credential compromise
- metadata enumeration at scale
- observability blind spots during active attack conditions

The goal is not only to patch isolated weaknesses, but to create a layered defense model that still functions under sustained abuse, regional failover, and adversaries willing to chain low-severity issues into high-impact incidents.

---

## Threat Model

### Adversary Classes

1. **Commodity attackers**
   - scan public endpoints
   - brute-force identifiers
   - exploit weak rate limits
   - replay leaked API keys

2. **Criminal operators**
   - use credential stuffing and purchased access
   - abuse signing quotas and public verification
   - spoof customer-facing webhooks
   - monetize service exhaustion or trust confusion

3. **State-capability adversaries**
   - operate globally distributed infrastructure
   - probe edge, origin, and service-to-service trust paths simultaneously
   - exploit fail-open behavior, DNS/egress gaps, and operational blind spots
   - combine API abuse, metadata collection, credential theft, and business disruption

### Assets To Protect

- signing integrity and provenance trust
- customer API keys and org-scoped permissions
- private service trust boundaries
- quota and billing integrity
- customer metadata and signing history
- public verification reliability under abuse
- webhook authenticity and delivery trust
- internal operational visibility during attack conditions

---

## Current State Assessment

| Concern | Current Reality | Risk | Priority |
|---------|-----------------|------|----------|
| Public verification rate limiting | In-memory IP-based limiter for some public routes; not consistently applied to all public verification paths | Multi-instance bypass, restart bypass, botnet evasion, resource exhaustion | P0 |
| Enterprise rate limiting | Enterprise and strategic partner tiers effectively unlimited | Stolen key can drive unbounded abuse | P0 |
| Image verification trust semantics | `db_confirmed` can cause `valid=true` even when cryptographic verification fails | Trust confusion, false positives, downstream misuse | P0 |
| Rich verification trust semantics | Returns trusted validity from stored records rather than current cryptographic proof | Weak verification guarantees | P0 |
| Webhook secret model | Secret stored hashed; dispatcher cannot sign outbound payloads | Customers cannot verify authenticity; spoofing risk | P0 |
| Internal service auth | Shared `internal_service_token` used across service boundaries | High blast radius if leaked | P0 |
| Permission vocabulary consistency | Mixed semantics like `lookup` vs `read` across auth paths | Authorization drift and bypass risk | P1 |
| Public metadata exposure | Public verify endpoints expose meaningful metadata | Enumeration and intelligence gathering | P1 |
| Outbound remote verification | Manifest fetches validate URL shape and cap size, but remain network-costly | Remote abuse and latency amplification | P1 |
| Abuse observability | Metrics exist, but attack-focused dashboards/alerts are not formalized | Slow detection and response | P1 |
| Control-plane resilience | Limited formalization for regional failover / degraded mode abuse handling | Operational fragility under state-scale attack | P1 |

---

## Objectives

- Prevent a single leaked credential from causing unbounded platform abuse.
- Ensure public verification remains available under globally distributed abuse.
- Make verification trust semantics explicit and cryptographically defensible.
- Provide webhook authenticity guarantees customers can actually verify.
- Replace broad shared internal trust with scoped, short-lived service authentication.
- Reduce metadata and oracle leakage from public surfaces.
- Build attack-aware observability, alerting, and response controls.
- Establish scalable control points at edge, app, and service layers.

---

## Non-Goals

- Eliminating all public verification features.
- Re-architecting the entire monorepo or replacing FastAPI.
- Building a full SIEM/SOC platform inside this PRD.
- Delivering customer-facing dashboard redesigns except where required for security controls.

---

## Requirements

### Functional Requirements

- All public verification routes must have distributed rate limiting and body-size enforcement.
- All authenticated routes must support per-key, per-org, and per-IP abuse controls.
- Verification responses must distinguish cryptographic validity from DB correlation.
- Webhook deliveries must be signed using retrievable, encrypted secrets.
- Internal service authentication must move to scoped, rotatable, short-lived trust.
- Permission enforcement must use a single canonical scope vocabulary.
- Public endpoints must support configurable metadata exposure modes.
- Security events must emit actionable telemetry for detection and response.

### Non-Functional Requirements

- Controls must work across horizontally scaled replicas.
- Abuse controls must degrade gracefully without taking the entire service down.
- Verification latency overhead should remain bounded and measurable.
- All critical hardening changes require automated tests before completion.
- Production rollout must support staged enablement and rollback.

---

## Work Breakdown Structure

### 1.0 Edge & Abuse-Prevention Foundation

- [ ] 1.1 Replace in-memory public rate limiting with distributed enforcement
  - [x] 1.1.1 Implement Redis-backed or gateway-backed public rate limit primitives for `verify_single`, `verify_batch`, `verify_image`, and `verify_rich`
  - [x] 1.1.2 Ensure limits are shared across replicas and survive process restarts
  - [x] 1.1.3 Add test coverage for multi-request window behavior — required: ✅ pytest
  - [ ] 1.1.4 Add load/abuse verification against concurrent clients — required: ✅ load test
- [ ] 1.2 Apply route-specific request size and cost ceilings
  - [ ] 1.2.1 Enforce request body limits at edge/proxy for all public verify endpoints
  - [x] 1.2.2 Add application-level payload caps for base64 image verification and batch verification
  - [x] 1.2.3 Reject oversized payloads with consistent 413 behavior — required: ✅ pytest
- [ ] 1.3 Add multi-dimensional authenticated throttling
  - [x] 1.3.1 Remove truly unlimited rate tiers; replace with high but finite ceilings
  - [x] 1.3.2 Rate limit by org, API key, user, IP, and endpoint scope
  - [ ] 1.3.3 Add burst and sustained windows separately
  - [ ] 1.3.4 Verify no high-tier key can bypass all protections — required: ✅ pytest ✅ load test
- [ ] 1.4 Add abuse-aware degradation modes
  - [ ] 1.4.1 Define degraded mode for expensive verification paths under overload
  - [ ] 1.4.2 Support temporary tightening of public endpoint limits via config/feature flag
  - [ ] 1.4.3 Document emergency traffic-control runbook — required: ✅ docs review

### 2.0 Verification Trust Model Hardening

- [ ] 2.1 Fix image verification truth semantics
  - [x] 2.1.1 Replace single `valid` truth source with explicit fields: `cryptographically_valid`, `db_matched`, `historically_signed_by_us`, `overall_status`
  - [x] 2.1.2 Prevent DB match from overriding failed cryptographic verification
  - [ ] 2.1.3 Update response schema and API docs — required: ✅ pytest ✅ docs review
- [ ] 2.2 Fix rich verification trust semantics
  - [x] 2.2.1 Remove implicit `valid=True` assumptions based only on stored signing-time data
  - [x] 2.2.2 Return explicit verification provenance for each sub-component
  - [x] 2.2.3 Add regression tests for tampered/stale record scenarios — required: ✅ pytest
- [ ] 2.3 Standardize verification language across API
  - [x] 2.3.1 Define canonical meanings for `valid`, `verified`, `trusted`, and `matched`
  - [x] 2.3.2 Audit public and internal endpoints for semantic consistency
  - [ ] 2.3.3 Update OpenAPI/docs examples — required: ✅ docs review

### 3.0 Credential, AuthN, and AuthZ Hardening

- [ ] 3.1 Harden API key abuse resistance
  - [ ] 3.1.1 Add per-key last-used telemetry and anomaly signals without synchronous hot-path DB contention
  - [ ] 3.1.2 Add suspicious-use detection for geo/IP diversity, burst anomalies, and scope misuse
  - [ ] 3.1.3 Define emergency key revoke/disable flow — required: ✅ pytest ✅ ops review
- [ ] 3.2 Unify permission vocabulary
  - [x] 3.2.1 Standardize canonical scopes (`sign`, `verify`, `lookup`, `read`, `admin`) and map legacy aliases explicitly
  - [x] 3.2.2 Audit all auth paths: key-service, auth-service JWT composition, demo mode, internal admin flow
  - [x] 3.2.3 Add contract tests proving equivalent enforcement across paths — required: ✅ pytest
- [ ] 3.3 Replace broad internal shared token trust
  - [x] 3.3.1 Design target model: mTLS or short-lived signed service JWTs with audience scoping
  - [ ] 3.3.2 Restrict internal endpoints by network policy plus service identity
  - [ ] 3.3.3 Add token rotation and revocation procedures
  - [ ] 3.3.4 Implement fallback plan for staged rollout — required: ✅ integration test ✅ docs review
- [ ] 3.4 Tighten demo and fallback behavior
  - [ ] 3.4.1 Audit all demo-key and failover paths for production fail-open risk
  - [ ] 3.4.2 Ensure production fallback behavior is explicit and deny-by-default
  - [ ] 3.4.3 Add tests for service-unavailable auth paths — required: ✅ pytest

### 4.0 Webhook Security & Outbound Trust

- [ ] 4.1 Fix webhook secret storage model
  - [x] 4.1.1 Store webhook secrets encrypted at rest, not hash-only
  - [ ] 4.1.2 Define secret rotation and re-display policy
  - [x] 4.1.3 Add migration plan for existing webhook records — required: ✅ migration test ✅ pytest
- [ ] 4.2 Sign all outbound webhook deliveries
  - [x] 4.2.1 Add HMAC signature headers using canonical payload serialization
  - [ ] 4.2.2 Add timestamp and replay-protection guidance for customers
  - [ ] 4.2.3 Publish verification examples in docs — required: ✅ pytest ✅ docs review
- [ ] 4.3 Strengthen outbound destination controls
  - [x] 4.3.1 Re-validate DNS/IP trust at delivery time and log resolved IPs
  - [ ] 4.3.2 Add egress policy guardrails for webhook dispatch
  - [ ] 4.3.3 Evaluate connect-by-IP/SNI-safe delivery strategy for high-trust mode
  - [x] 4.3.4 Add tests for private-IP / localhost / redirect rejection — required: ✅ pytest
- [ ] 4.4 Add outbound delivery safety limits
  - [ ] 4.4.1 Constrain concurrency, retry storms, and per-org webhook fan-out
  - [ ] 4.4.2 Add circuit-breaking for chronically failing destinations
  - [ ] 4.4.3 Ensure attack traffic on customer webhooks cannot starve core API capacity — required: ✅ load test

### 5.0 Public Surface Minimization

- [ ] 5.1 Review public metadata exposure
  - [x] 5.1.1 Inventory all fields returned from public verification endpoints
  - [ ] 5.1.2 Classify fields as public-by-default, opt-in, or restricted
  - [x] 5.1.3 Add config/tenant controls for minimal public responses — required: ✅ product review ✅ pytest
- [ ] 5.2 Reduce oracle behavior
  - [x] 5.2.1 Normalize error shapes and timing where practical for existence checks
  - [ ] 5.2.2 Audit identifier formats and predictability for public lookup paths
  - [x] 5.2.3 Add enumeration-resistance tests — required: ✅ pytest
- [ ] 5.3 Secure docs and discovery surfaces
  - [x] 5.3.1 Review `/docs`, `/metrics`, `/health`, `/readyz` exposure policy in production
  - [x] 5.3.2 Restrict sensitive operational metadata where not required publicly
  - [ ] 5.3.3 Confirm metrics endpoint protection strategy at infra layer — required: ✅ ops review

### 6.0 Expensive Verification Path Resilience

- [ ] 6.1 Add bounded concurrency for remote/expensive verification paths
  - [x] 6.1.1 Add per-process and shared concurrency guards for manifest fetch/verify work
  - [x] 6.1.2 Add budgets and short-circuit behavior under overload
  - [ ] 6.1.3 Validate fairness so one tenant cannot starve others — required: ✅ load test
- [ ] 6.2 Improve remote manifest verification controls
  - [x] 6.2.1 Cache positive and negative verification outcomes where safe
  - [ ] 6.2.2 Add host-level circuit breaking and timeout telemetry
  - [x] 6.2.3 Ensure remote verification failures never become silent success states — required: ✅ pytest
- [ ] 6.3 Tamper and parser hardening
  - [ ] 6.3.1 Add malformed payload corpus for manifests and images
  - [ ] 6.3.2 Add regression tests for parser bombs / oversized nested structures
  - [ ] 6.3.3 Validate logging does not leak untrusted payloads — required: ✅ pytest

### 7.0 Detection, Response, and Security Telemetry

- [ ] 7.1 Create attack-focused telemetry model
  - [ ] 7.1.1 Emit counters for public verification failures, auth failures, rate-limit hits, webhook rejections, internal auth failures
  - [ ] 7.1.2 Add labels for route, org, key prefix, trust result, and abuse reason where safe
  - [ ] 7.1.3 Validate low-cardinality metric design — required: ✅ observability review
- [ ] 7.2 Build alerts and dashboards
  - [ ] 7.2.1 Alert on public verification spikes, enterprise-key anomaly bursts, webhook destination churn, and internal token misuse
  - [ ] 7.2.2 Create dashboards for active attack triage
  - [ ] 7.2.3 Add SLO views for degraded-mode operation — required: ✅ alert test ✅ dashboard review
- [ ] 7.3 Incident response readiness
  - [ ] 7.3.1 Define playbooks for key leak, public endpoint flood, webhook abuse, and internal token compromise
  - [ ] 7.3.2 Define kill switches / feature flags for rapid containment
  - [ ] 7.3.3 Run tabletop exercise — required: ✅ exercise completed

### 8.0 Global-Scale Resilience & Rollout

- [ ] 8.1 Formalize control points by layer
  - [ ] 8.1.1 Edge/CDN protections
  - [ ] 8.1.2 API gateway throttles and payload filtering
  - [ ] 8.1.3 Application-layer trust enforcement
  - [ ] 8.1.4 Service-to-service identity controls
- [ ] 8.2 Stage rollout safely
  - [ ] 8.2.1 Ship feature flags for new rate-limit and auth models
  - [ ] 8.2.2 Roll out shadow metrics before hard enforcement where possible
  - [ ] 8.2.3 Define rollback criteria per phase — required: ✅ rollout review
- [ ] 8.3 Validate worldwide-scale readiness
  - [ ] 8.3.1 Run geographically distributed load simulation
  - [ ] 8.3.2 Validate multi-replica consistency of rate limiting and abuse decisions
  - [ ] 8.3.3 Confirm failover behavior under regional disruption — required: ✅ load test ✅ game day

---

## Milestones

| Milestone | Scope | Exit Criteria |
|-----------|-------|---------------|
| M0 | Threat model + design lock | PRD approved; architecture decisions made for distributed limiting, webhook secret storage, and internal auth target model |
| M1 | P0 abuse controls | Distributed public limiting, finite authenticated throttles, payload caps live behind flags |
| M2 | Trust model fixes | Image/rich verification semantics corrected and documented |
| M3 | Credential + webhook hardening | Internal auth migration path implemented; outbound webhooks signed |
| M4 | Detection + response | Dashboards, alerts, playbooks, kill switches in place |
| M5 | State-actor readiness validation | Global load/game-day exercises complete; rollout accepted |

---

## Success Criteria

- Public verification remains available and bounded under distributed attack traffic.
- No tier or key class bypasses all abuse controls.
- Verification APIs never report cryptographic validity based solely on DB correlation.
- Webhook customers can verify authenticity of all outbound deliveries.
- Internal privileged service calls use scoped, rotatable, short-lived trust.
- Attack dashboards and alerts provide actionable visibility within minutes.
- All completed tasks are backed by tests and/or operational validation markers.

---

## Risks & Mitigations

- **Operational complexity increases**
  - Mitigation: stage behind flags, shadow mode first, document rollback paths.
- **Breaking API contract changes in verification responses**
  - Mitigation: additive schema where possible, version documented semantics, customer migration guide.
- **Distributed rate limiting can introduce false positives**
  - Mitigation: tune in observe-only mode first and keep emergency overrides.
- **Internal auth migration may impact service reliability**
  - Mitigation: dual-stack old/new auth during transition with strong observability.
- **Webhook secret migration may affect existing customers**
  - Mitigation: backward-compatible rollout with transition headers and documentation.

---

## Open Questions

1. Should state-scale abuse controls primarily live at CDN/gateway, app layer, or both by default?
2. What target internal auth model do we want to standardize on: mTLS, signed service JWTs, or platform workload identity?
3. Do we want to preserve a legacy `valid` field for backward compatibility, or force consumers onto more explicit trust fields?
4. Should public verification offer tenant-configurable anonymity / metadata minimization modes?
5. What global traffic simulation environment will be our source of truth for readiness sign-off?

---

## Completion Notes

- This PRD is the SSOT for active security hardening work on `enterprise_api`.
- No task may be marked complete without the verification marker(s) listed under that task.
- Follow-on `.teams/TEAM_*.md` files should reference this PRD task numbering rather than restating scope.
