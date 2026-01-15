# Web Service Form Routing & Microservices Consistency Audit

**Status:** 🔄 In Progress
**Current Goal:** 1.1 — Align marketing form routing with web-service and Traefik

## Overview

Marketing-site form submissions are not consistently routed to the web-service in production, and routing/docs drift exists across microservices and Traefik configs. This PRD aligns request routing, adds missing gateway routes, and audits documentation for consistency.

## Objectives

- Ensure marketing forms consistently reach web-service endpoints in all environments.
- Standardize Traefik routing and service ownership for web-service endpoints.
- Update documentation to reflect the canonical routing and environment variables.

## Tasks

### 1.0 Routing & Service Ownership

- [ ] 1.1 Align marketing-site form proxy (`/api/demo-request`) with web-service endpoints.
- [ ] 1.2 Add Traefik routing for web-service endpoints in local + Railway gateway configs.
- [ ] 1.3 Normalize client form submission paths for AI/publisher demos and sales inquiries.

### 2.0 Documentation & Env Audit

- [ ] 2.1 Update marketing-site env examples to document `WEB_SERVICE_URL` usage.
- [ ] 2.2 Update web-service env docs to reflect `EMAIL_FROM_NAME` usage.
- [ ] 2.3 Update microservices docs (README + architecture) to include web-service routing.

### 3.0 Testing & Validation

- [ ] 3.1 Unit tests passing — ✅ pytest / ✅ npm test (as applicable)
- [ ] 3.2 Frontend verification — ✅ puppeteer

## Success Criteria

- Form submissions reach web-service endpoints in production routing.
- Traefik routing explicitly maps web-service endpoints in local + Railway configs.
- Documentation reflects consistent service ownership and env vars.
- Tests pass with verification markers.

## Completion Notes

(Filled when PRD is complete.)
