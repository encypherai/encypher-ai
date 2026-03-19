# PRD: Enterprise Rollout Readiness

**Status:** Complete
**Current Goal:** All P0 and P1 items implemented
**Team:** TEAM_258

## Overview
Close remaining gaps for enterprise-scale rollout. The platform is architecturally mature but specific gaps block enterprise pilot sales. Backend services are largely complete; most work is dashboard UI wiring and one backend feature (IP allowlisting).

## Objectives
- Enable BYOK key management through dashboard UI
- Wire Stripe Connect payout flow end-to-end
- Add IP allowlisting to API keys for enterprise security review
- Split settings into personal vs organization admin
- Add image signing dashboard UI
- Add print leak detection workflow UI
- Add GDPR data deletion workflow
- Add seat management upgrade flow

## Tasks

### P0: Blocks Enterprise Pilot

- [x] 1.0 BYOK Certificate Management UI -- pytest N/A (UI), tsc clean
  - [x] 1.1 Add ByokKeyManagementCard to settings page
  - [x] 1.2 Register public key form (PEM input, key name, algorithm select)
  - [x] 1.3 List registered keys (fingerprint, algorithm, status, expiry)
  - [x] 1.4 Revoke key with reason dialog
  - [x] 1.5 View trusted CAs list

- [x] 2.0 Stripe Connect Payout Wiring -- tsc clean
  - [x] 2.1 Add Connect onboarding endpoint to billing-service
  - [x] 2.2 Wire dashboard button to trigger Connect onboarding
  - [x] 2.3 Handle return/refresh URLs
  - [x] 2.4 Show connection status after return

- [x] 3.0 API Key IP Allowlisting -- pytest 12/12, tsc clean
  - [x] 3.1 Add ip_allowlist field to API key model/schema
  - [x] 3.2 IP check middleware in dependencies.py
  - [x] 3.3 Dashboard IP allowlist input on API key create/edit
  - [x] 3.4 Support IPv4 and IPv6 CIDR notation
  - [x] 3.5 Tests for IP allowlisting (12 tests)

### P1: Expected by Enterprise Buyers

- [x] 4.0 Organization Administration Page -- tsc clean
  - [x] 4.1 Create /settings/organization/page.tsx
  - [x] 4.2 Security policies section
  - [x] 4.3 Default signing config section
  - [x] 4.4 Feature overview and add-ons status
  - [x] 4.5 Role-gated visibility (owner/admin only)

- [x] 5.0 Image Signing Dashboard UI -- tsc clean
  - [x] 5.1 Create /image-signing/page.tsx
  - [x] 5.2 Image upload dropzone
  - [x] 5.3 Signing options (C2PA, watermark)
  - [x] 5.4 Signed image download
  - [x] 5.5 Verification result display

- [x] 6.0 Print Leak Detection Workflow UI -- tsc clean
  - [x] 6.1 Create /print-detection/page.tsx
  - [x] 6.2 List fingerprinted documents
  - [x] 6.3 Upload scanned document for source ID
  - [x] 6.4 Detection results view

- [x] 7.0 GDPR Data Deletion Workflow -- pytest 22/22, tsc clean
  - [x] 7.1 User account deletion request in settings
  - [x] 7.2 Org admin purge user data
  - [x] 7.3 Deletion cascade across services
  - [x] 7.4 Create data_management.py router (6 endpoints)
  - [x] 7.5 Deletion confirmation/receipt

- [x] 8.0 Seat Management Upgrade Flow -- tsc clean
  - [x] 8.1 Upgrade CTA when seats full on team page
  - [x] 8.2 Deep link to billing with upgrade pre-selected
  - [x] 8.3 Seat count selection on upgrade flow

## Success Criteria
- [x] All P0 items complete with passing tests
- [x] Dashboard builds clean (`next build`)
- [x] No regressions in existing functionality
- [x] Enterprise security review requirements met (IP allowlisting)

## Completion Notes
Completed 2026-03-18 by TEAM_258 using 4 parallel agents.

**34 new tests:** 12 IP allowlist + 22 GDPR data management, all passing.

**New pages:** /settings/organization, /image-signing, /print-detection

**New backend:** data_management.py router (6 GDPR endpoints), IP allowlist check in dependencies.py, Connect onboarding endpoint in billing-service

**Modified:** settings/page.tsx (BYOK card, account deletion), billing/page.tsx (Stripe Connect, seat upgrade), api-keys/page.tsx (IP allowlist), team/page.tsx (seat upgrade CTA), DashboardLayout.tsx (nav items), api.ts (BYOK, image signing, print detection, GDPR, Stripe Connect, IP allowlist methods)
