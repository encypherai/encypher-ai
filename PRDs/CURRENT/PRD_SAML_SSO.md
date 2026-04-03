# SAML SSO / Enterprise Identity Provider Integration

**Status:** Planned
**Current Goal:** PRD complete, frontend scaffolding in place, backend implementation pending
**Priority:** P2 (enterprise sales blocker)

## Overview

Enterprise buyers require SAML SSO integration with their identity provider (Okta, Azure AD, Google Workspace, OneLogin) as a procurement prerequisite. The dashboard already supports Google OAuth, GitHub OAuth, and Passkey authentication. SAML SSO adds the enterprise identity federation layer that Fortune 500 security questionnaires require.

## Objectives

- Allow organization admins to configure SAML SSO for their organization
- Support IdP-initiated and SP-initiated SAML 2.0 flows
- Enforce SSO-only login for organizations that enable it (disable email/password for org members)
- Provide self-service SAML configuration with metadata URL or manual entry
- Support the major enterprise IdPs: Okta, Azure AD, Google Workspace, OneLogin

## Tasks

### 1.0 Backend - Auth Service

- [ ] 1.1 Add SAML SSO configuration model (org_id, idp_metadata_url, idp_entity_id, idp_sso_url, idp_certificate, sp_entity_id, sp_acs_url, enabled, enforce_sso, created_at)
- [ ] 1.2 Add SAML SSO CRUD endpoints (POST/GET/PUT/DELETE /api/v1/organizations/{org_id}/sso)
- [ ] 1.3 Implement SP-initiated SAML flow (redirect to IdP, consume assertion at ACS endpoint)
- [ ] 1.4 Implement IdP-initiated SAML flow (accept unsolicited assertions at ACS endpoint)
- [ ] 1.5 Map SAML attributes to user profile (email, name, groups)
- [ ] 1.6 Auto-provision users on first SAML login (JIT provisioning)
- [ ] 1.7 Enforce SSO-only login when organization has enforce_sso=true (reject email/password for org domain)
- [ ] 1.8 Add SAML metadata endpoint (GET /api/v1/saml/metadata) for IdP configuration
- [ ] 1.9 Add database migration for SSO configuration table

### 2.0 Frontend - SSO Admin Configuration

- [ ] 2.1 Add SSO tab to Settings > Organization page
- [ ] 2.2 Build SAML configuration form (metadata URL import or manual entry)
- [ ] 2.3 Show SP metadata (Entity ID, ACS URL, Certificate) for IdP configuration
- [ ] 2.4 Add "Test SSO Connection" flow with dry-run validation
- [ ] 2.5 Add "Enforce SSO" toggle with confirmation dialog
- [ ] 2.6 Show SSO status badge on organization settings

### 3.0 Frontend - Login Flow

- [ ] 3.1 Add "Sign in with SSO" button to login page
- [ ] 3.2 Add email domain detection to auto-redirect to SSO for enforced orgs
- [ ] 3.3 Handle SAML callback and session creation on frontend
- [ ] 3.4 Show appropriate error messages for SAML failures

### 4.0 Testing

- [ ] 4.1 Unit tests for SAML assertion parsing and validation
- [ ] 4.2 Integration tests with mock IdP
- [ ] 4.3 E2E test: configure SSO, login via SSO, enforce SSO
- [ ] 4.4 Security review: assertion replay, signature validation, audience restriction

## Technical Notes

- Python SAML library: `python3-saml` or `pysaml2` (evaluate both; python3-saml is lighter)
- ACS URL format: `https://api.encypher.com/api/v1/saml/acs`
- SP Entity ID format: `https://api.encypher.com/saml/metadata`
- NextAuth.js supports custom providers - SAML callback can be wired through a custom provider
- Session tokens from SAML should be equivalent to existing JWT sessions (same claims, same expiry)

## Success Criteria

- [ ] Organization admin can configure SAML SSO from Settings > Organization > SSO tab
- [ ] Users can log in via "Sign in with SSO" on the login page
- [ ] Enforce SSO mode blocks email/password login for org domain members
- [ ] JIT provisioning creates user accounts on first SAML login
- [ ] SP metadata endpoint allows IdP admins to configure their side automatically
