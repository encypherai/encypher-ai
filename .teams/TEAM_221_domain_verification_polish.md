# TEAM_221 — Domain Verification Polish

## Session Start
Date: 2026-02-21
Branch: feature/rights-management-system

## Objective
Polish domain verification UX based on audit findings:
1. Email template: reframe as DNS setup instructions (not "click to verify")
2. Settings Organization tab: copy + UX polish (labels, copy-to-clipboard, badges, ToggleSwitch, empty state, inline DNS card)
3. /verify-domain public landing page: new page that receives email links gracefully

## Tasks
- [x] Step 1: Email template in organizations.py -- pytest 211 passed
- [x] Step 2: Settings org tab polish in settings/page.tsx -- tsc clean
- [x] Step 3: New public landing page apps/dashboard/src/app/verify-domain/page.tsx -- tsc clean
- [x] Verification: tsc --noEmit (zero errors), pytest (211 passed, 0 failed)

## Status
COMPLETE

## Changes Made

### services/auth-service/app/api/v1/organizations.py
- `_send_domain_claim_email()`: added `dns_token` param; subject changed to "Set up DNS
  verification for {domain}"; body now leads with DNS TXT record in `<pre>` block, primary
  CTA points to `/settings?tab=organization`, email_token link demoted to optional audit trail
- Call site at ~line 634: added `dns_token=claim.dns_token`

### apps/dashboard/src/app/settings/page.tsx
- Added imports: `Copy`, `Check` from lucide-react; `DomainClaimInfo` type from api
- Added state: `newlyCreatedClaim: DomainClaimInfo | null`, `copiedId: string | null`
- `createDomainClaimMutation.onSuccess`: saves response.data to newlyCreatedClaim, fixed toast
- `verifyDnsMutation.onSuccess`: fixed toast ("DNS record not yet detected..." vs "Domain verified.")
- Anonymous publisher: replaced raw `<input type="checkbox">` with `<ToggleSwitch>`
- "Verification email" label -> "Contact email" with helper text
- "Request verification" button -> "Add domain"
- After successful add: inline amber DNS instruction card with copy button (dismissible)
- Domain claims list: colored status badges (amber=Pending DNS, emerald=Verified+date, red=Check failed)
- Each claim row: copy-to-clipboard button for TXT record (Copy/Check icon toggle)
- Empty state: centered message "No domains added yet. Add your first domain..."
- Verified claims no longer show redundant Verify DNS button

### apps/dashboard/src/app/verify-domain/page.tsx (NEW)
- Public page, no auth required, wrapped in Suspense for useSearchParams
- Reads `?token=` param, calls GET /api/v1/organizations/domain-claims/verify-email?token=...
- States: loading spinner -> success card (with DNS next-steps + Go to Settings CTA) or error card
- Matches login page aesthetic: centered white card on gradient background

## Suggested Commit Message
```
feat(domain): polish verification UX - DNS-first email, settings improvements, /verify-domain page

- Email: reframe to DNS setup instructions (TXT record in pre block, Settings CTA primary,
  audit link secondary); add dns_token param to _send_domain_claim_email()
- Settings org tab: colored status badges (amber/emerald/red), copy-to-clipboard for TXT records,
  inline DNS card after domain add, Contact email label + helper, Add domain button copy,
  anonymous publisher raw checkbox -> ToggleSwitch, improved empty state
- New /verify-domain public page: receives email links, calls verify-email endpoint, shows
  success/error states with DNS next-step guidance and Go to Settings CTA
```
