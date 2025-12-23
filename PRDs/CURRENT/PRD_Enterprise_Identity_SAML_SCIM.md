# Enterprise Identity: SAML SSO + SCIM Provisioning

**Status:** 🚧 In Progress  
**Current Goal:** Task 3.0–4.0 — Contract-tested SAML + SCIM endpoints in `auth-service`.

## Overview

Enterprise publishers require SAML-based SSO (Okta/Azure AD/Google Workspace) and automated user provisioning (SCIM) to onboard teams securely and at scale. This PRD defines the identity features needed to support enterprise authentication, authorization, and admin workflows across Encypher services.

## Objectives

- Enable SAML 2.0 SSO for enterprise organizations with per-tenant configuration
- Enable SCIM 2.0 provisioning for Users and Groups with least-privilege access
- Ensure robust RBAC (org-level + team-level) across signing, verification, and admin endpoints
- Provide auditability and operational visibility for identity events

## Tasks

### 1.0 Requirements, Threat Model, and Architecture

- [ ] 1.1 Identify and document supported Identity Providers (IdPs)
  - [ ] 1.1.1 Okta
  - [ ] 1.1.2 Azure AD / Entra
  - [ ] 1.1.3 Google Workspace
  - [ ] 1.1.4 OneLogin (optional)
- [ ] 1.2 Define SAML flows to support
  - [ ] 1.2.1 SP-initiated login
  - [ ] 1.2.2 IdP-initiated login
  - [ ] 1.2.3 Optional SLO (single logout)
- [ ] 1.3 Define attribute mapping contract
  - [ ] 1.3.1 Required: `email`
  - [ ] 1.3.2 Optional: `first_name`, `last_name`, `display_name`
  - [ ] 1.3.3 Role mapping via group/attribute (e.g., `roles`, `groups`)
- [ ] 1.4 Define tenant isolation invariants
  - [ ] 1.4.1 Map SAML assertions to an `organization_id` deterministically
  - [ ] 1.4.2 Enforce `audience` + `recipient` validation
  - [ ] 1.4.3 Enforce signed assertions and signed responses
- [ ] 1.5 Threat model and security requirements
  - [ ] 1.5.1 Replay prevention (NotBefore/NotOnOrAfter + assertion ID cache)
  - [ ] 1.5.2 Clock skew policy
  - [ ] 1.5.3 Key rollover plan (IdP signing cert rotation)
  - [ ] 1.5.4 Strict redirect allowlist
  - [ ] 1.5.5 Audit events for login/provisioning
- [ ] 1.6 Decide service ownership
  - [ ] 1.6.1 SAML endpoints live in `auth-service`
  - [x] 1.6.2 SCIM endpoints live in `auth-service` — ✅ pytest
  - [ ] 1.6.3 Enterprise API consumes identity via JWT and org/team claims

### 2.0 Data Model + Configuration (Tenant Settings)

- [ ] 2.1 Add organization-level SSO configuration fields (SSOT: organization settings)
  - [ ] 2.1.1 `sso_enabled: bool`
  - [ ] 2.1.2 `saml_enabled: bool`
  - [ ] 2.1.3 `saml_entity_id: str`
  - [ ] 2.1.4 `saml_acs_url: str`
  - [ ] 2.1.5 `saml_metadata_url: str` (optional)
  - [ ] 2.1.6 `saml_idp_entity_id: str`
  - [ ] 2.1.7 `saml_idp_sso_url: str`
  - [ ] 2.1.8 `saml_idp_x509_cert_pem: text`
  - [ ] 2.1.9 `saml_require_signed_assertions: bool`
  - [ ] 2.1.10 `saml_email_attribute: str` (default `email`)
- [ ] 2.2 Add organization-level SCIM configuration
  - [ ] 2.2.1 `scim_enabled: bool`
  - [ ] 2.2.2 `scim_bearer_token_hash: str`
  - [ ] 2.2.3 `scim_base_url: str`
  - [ ] 2.2.4 Token rotation support (multiple active tokens with expiry)
- [ ] 2.3 Add migrations and backfills
- [ ] 2.4 Add admin APIs to manage these settings (auth required, org-admin scope)

### 3.0 SAML 2.0 Implementation (Auth Service)

- [ ] 3.1 Select SAML library and implement POC (pysaml2 vs python3-saml)
- [ ] 3.2 Implement Service Provider (SP) metadata endpoint
  - [x] 3.2.1 `GET /api/v1/auth/saml/metadata?org_id=...` — ✅ pytest
  - [ ] 3.2.2 Include ACS URL, entity ID, certificate
- [ ] 3.3 Implement SAML login initiation
  - [x] 3.3.1 `GET /api/v1/auth/saml/login?org_id=...&return_to=...` — ✅ pytest
  - [ ] 3.3.2 Persist relay state safely (nonce + allowlisted domains)
- [ ] 3.4 Implement Assertion Consumer Service (ACS)
  - [x] 3.4.1 `POST /api/v1/auth/saml/acs` — ✅ pytest
  - [ ] 3.4.2 Validate signatures + conditions + audience + recipient
  - [ ] 3.4.3 Resolve or auto-create user (policy-driven)
  - [ ] 3.4.4 Issue Encypher JWT session (include org + role claims)
- [ ] 3.5 Implement IdP-initiated flow support
- [ ] 3.6 Implement optional Single Logout (SLO) (if required by enterprise deals)
- [ ] 3.7 Add comprehensive audit events
  - [ ] 3.7.1 `auth.saml.login.success`
  - [ ] 3.7.2 `auth.saml.login.failure`
  - [ ] 3.7.3 `auth.saml.config.updated`

### 4.0 SCIM 2.0 Provisioning (Auth Service)

- [x] 4.1 Implement SCIM auth (bearer token per organization) — ✅ pytest
- [ ] 4.2 Implement SCIM Users endpoints
  - [x] 4.2.1 `GET /scim/v2/Users` — ✅ pytest
  - [x] 4.2.2 `POST /scim/v2/Users` — ✅ pytest
  - [x] 4.2.3 `GET /scim/v2/Users/{id}` — ✅ pytest
  - [ ] 4.2.4 `PATCH /scim/v2/Users/{id}`
  - [ ] 4.2.5 `DELETE /scim/v2/Users/{id}` (deactivate)
- [ ] 4.3 Implement SCIM Groups endpoints
  - [ ] 4.3.1 `GET /scim/v2/Groups`
  - [ ] 4.3.2 `POST /scim/v2/Groups`
  - [ ] 4.3.3 `PATCH /scim/v2/Groups/{id}`
  - [ ] 4.3.4 `DELETE /scim/v2/Groups/{id}`
- [ ] 4.4 Map SCIM groups → Encypher teams/roles
  - [ ] 4.4.1 Team creation policy
  - [ ] 4.4.2 Role assignment policy
- [ ] 4.5 Idempotency and concurrency controls
  - [ ] 4.5.1 ExternalId support
  - [ ] 4.5.2 ETags/If-Match where applicable
  - [x] 4.5.3 SCIM Users membership insert is idempotent — ✅ pytest
- [ ] 4.6 Audit events
  - [ ] 4.6.1 `scim.user.created/updated/deactivated`
  - [ ] 4.6.2 `scim.group.created/updated/deleted`

### 5.0 RBAC and Authorization Hardening

- [ ] 5.1 Define and document org roles
  - [ ] 5.1.1 `owner`, `admin`, `editor`, `viewer`
- [ ] 5.2 Define and document API scopes
  - [ ] 5.2.1 `sign:write`, `verify:read`, `keys:write`, `org:admin`, `billing:admin`
- [ ] 5.3 Enforce RBAC across key admin endpoints
- [ ] 5.4 Ensure audit logs capture actor identity (user vs API key)

### 6.0 Dashboard UX (Enterprise Admin)

- [ ] 6.1 Add SAML configuration wizard
  - [ ] 6.1.1 Upload IdP certificate
  - [ ] 6.1.2 Copy SP metadata
  - [ ] 6.1.3 Test login button
- [ ] 6.2 Add SCIM configuration page
  - [ ] 6.2.1 Generate/rotate SCIM token
  - [ ] 6.2.2 Copy SCIM base URL
  - [ ] 6.2.3 Show setup instructions for Okta/Azure
- [ ] 6.3 Add audit view for identity events

### 7.0 Testing & Validation

- [x] 7.1 Unit tests passing — ✅ pytest
- [ ] 7.2 Integration tests passing — ✅ pytest
- [ ] 7.3 Dashboard verification — ✅ puppeteer
- [ ] 7.4 Security validation checklist
  - [ ] 7.4.1 Assertion signature validation
  - [ ] 7.4.2 Replay protection verified
  - [x] 7.4.3 Open redirect prevention verified — ✅ pytest
  - [x] 7.4.4 Sensitive request logging redaction verified — ✅ pytest

## Success Criteria

- Enterprise org can enable SAML SSO and successfully authenticate via Okta and Azure AD
- SCIM provisioning can create/update/deactivate users and manage groups/teams
- RBAC prevents unauthorized access to admin and key-management endpoints
- Audit logs record identity events with actor attribution
- All tests passing with verification markers

## Completion Notes

(Filled when PRD is complete.)
