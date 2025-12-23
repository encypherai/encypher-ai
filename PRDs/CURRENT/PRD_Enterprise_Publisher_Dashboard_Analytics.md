# Enterprise Publisher Dashboard + Verification Analytics

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Define the minimum dashboard views required for enterprise publishers to manage provenance at scale.

## Overview

Enterprise publishers need visibility into signed content coverage, verification activity, revocations, and licensing signals. This PRD defines dashboard features and analytics required for operational adoption.

## Objectives

- Provide publishers a content portfolio view (signed vs unsigned)
- Provide verification analytics (volume, sources, geography)
- Provide revocation visibility and workflows
- Provide exportable reports for compliance

## Tasks

### 1.0 Metrics Model & Event Collection

- [ ] 1.1 Define verification event schema
- [ ] 1.2 Track verification events by
  - [ ] 1.2.1 document_id
  - [ ] 1.2.2 signer_id
  - [ ] 1.2.3 source (API/widget/extension)
  - [ ] 1.2.4 geo (country)
- [ ] 1.3 Track signing events (per org)
- [ ] 1.4 Define retention policy for analytics

### 2.0 Dashboard Views

- [ ] 2.1 Portfolio overview
- [ ] 2.2 Signed content list + search
- [ ] 2.3 Verification analytics dashboards
- [ ] 2.4 Revocation dashboards
- [ ] 2.5 Export reports (CSV/PDF)

### 3.0 Alerts

- [ ] 3.1 Unusual verification spikes
- [ ] 3.2 Potential tampering patterns
- [ ] 3.3 Revocation propagation monitoring

### 4.0 RBAC + Team Views

- [ ] 4.1 Role-based access for dashboards
- [ ] 4.2 Team-level scoping

### 5.0 Testing & Validation

- [ ] 5.1 Unit tests passing — ✅ pytest
- [ ] 5.2 Dashboard verification — ✅ puppeteer

## Success Criteria

- Enterprise org can view signing coverage and verification activity
- Reports support procurement/compliance needs
- Alerts provide actionable signals

## Completion Notes

(Filled when PRD is complete.)
