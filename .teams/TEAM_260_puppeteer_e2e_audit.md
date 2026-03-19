# TEAM_260 -- Puppeteer E2E Audit of TEAM_258/259 Pages

## Status: COMPLETE

## Summary
Comprehensive Puppeteer E2E audit of all pages built in TEAM_258 (Enterprise Rollout) and TEAM_259 (Scale Prep). Tested as both free-tier and enterprise-tier users.

---

## Pages Tested

### 1. Settings - Profile Tab (`/settings`)
- **Status**: PASS
- Profile form renders correctly with name, email, company, phone, job title
- Delete Account section visible at bottom with GDPR 90-day soft-delete explanation
- "Delete my account" button opens confirmation dialog with:
  - "Are you sure?" prompt with detailed explanation
  - Reason (optional) textarea
  - "Type DELETE to confirm" input
  - "Confirm deletion" and "Cancel" buttons
- Cancel button works correctly

### 2. Settings - Organization Tab (in-page)
- **Status**: CRITICAL BUG
- Clicking the "Organization" tab in Settings causes immediate session expiration
- Redirects to `/login?reason=session_expired`
- Reproducible on both free and enterprise tier
- Root cause investigation: likely the `ByokKeyManagementCard` component's `keysQuery` (calls `apiClient.listPublicKeys`) fires when the tab mounts. If the API returns 401 (likely due to token format mismatch), the global QueryClient retry handler in `providers.tsx` calls `isSessionExpiredError()` which returns true for generic 401s, triggering a full sign-out.
- **Also**: The `?tab=organization` URL param is not honored -- the settings page useEffect only handles `?tab=billing`.

### 3. Settings Organization Admin (`/settings/organization`)
- **Status**: PARTIAL -- redirects to `/settings` for both free and enterprise users
- Free tier: correctly redirects (not admin)
- Enterprise tier (owner): INCORRECTLY redirects. The `useCurrentUserRole` hook should detect the user as owner/admin but the redirect fires before the org members query completes. Race condition between org context loading and the redirect useEffect.

### 4. Image Signing (`/image-signing`)
- **Status**: PASS
- Upload dropzone renders correctly
- Signing options panel shows:
  - C2PA Manifest toggle (enabled by default)
  - TrustMark Watermark with "Enterprise" badge (disabled, correctly gated)
  - Attribution Indexing toggle (enabled by default)
  - Image Quality slider at 95%
  - Document Title input

### 5. Print Leak Detection (`/print-detection`)
- **Status**: PASS
- Free tier: Shows Enterprise upgrade gate with "Upgrade to Enterprise" button
- Enterprise tier: Shows full content with:
  - "Scan for Fingerprint" textarea
  - "Scan for Source" button
  - "Fingerprinted Documents" section
  - Character counter

### 6. API Keys (`/api-keys`)
- **Status**: PASS
- Empty state renders with "No API Keys Yet" and "Generate Your First Key" button
- Create modal includes:
  - Name input with placeholder
  - IP Allowlist (optional) textarea with CIDR examples
  - Helper text explaining format
  - Cancel and Create Key buttons

### 7. Billing (`/billing`)
- **Status**: PASS
- Current Plan section shows Free / Active
- Usage This Period with correct limits (1,000 C2PA, 10,000 sentences, unlimited API/verifications)
- Coalition Earnings with $0.00 / Not Connected payout
- "Connect Payout Account" button (NOT "Coming Soon" -- correct)
- Licensing Revenue section with publisher/self-service split explanation
- Add-Ons & Bundles section

### 8. Team (`/team`)
- **Status**: PASS
- Free tier: Shows Enterprise upgrade gate
- Enterprise tier: Full team management with:
  - Team Seats: 1/1 "Seat limit reached" + "Upgrade Seats" CTA
  - Create Organization, Invite Member, Bulk Invite buttons
  - API Keys by Member section
  - Team Members list showing owner

### 9. CDN Analytics (`/cdn-analytics`)
- **Status**: PASS
- Free tier: Shows Enterprise upgrade gate
- Enterprise tier: Shows "No CDN Data Yet" with "Set Up CDN Integration" button
- Sidebar correctly shows ENTERPRISE section items

### 10. Webhooks (`/webhooks`)
- **Status**: PASS (with note)
- Renders for ALL tiers (not enterprise-gated)
- Empty state with "No webhooks configured" and "Create Your First Webhook"
- Documentation section with "View documentation" link
- Note: May need enterprise gating if intended to be enterprise-only

---

## Issue Summary

### CRITICAL
1. **Settings Organization tab causes session logout** -- Clicking the Organization tab in `/settings` redirects to `/login?reason=session_expired`. Affects all tiers. Likely caused by `ByokKeyManagementCard` query triggering false session-expiry detection in global error handler.
   - File: `/apps/dashboard/src/app/settings/page.tsx` (lines 310-326, 2288-2289)
   - File: `/apps/dashboard/src/components/providers.tsx` (lines 38-43)
   - File: `/apps/dashboard/src/lib/session-errors.ts`

### HIGH
2. **Settings Organization Admin page inaccessible** -- `/settings/organization` always redirects to `/settings` even for enterprise owners. Race condition between org context loading and redirect useEffect.
   - File: `/apps/dashboard/src/app/settings/organization/page.tsx` (lines 602-608)

### MEDIUM
3. **Settings `?tab=organization` URL param not supported** -- The settings page only handles `?tab=billing` in its useEffect (line 932). Links using `?tab=organization` from other pages don't work.
   - File: `/apps/dashboard/src/app/settings/page.tsx` (lines 929-940)

4. **Webhooks not enterprise-gated** -- Accessible to free-tier users. If this is intentional, no action needed. If it should be enterprise-only (as suggested in the sidebar placement under ENTERPRISE section), a tier gate should be added.

### LOW
5. **Billing page missing "Billing" link in sidebar for enterprise tier** -- When on enterprise, sidebar shows Settings but not Billing under ACCOUNT section.

---

## Recommended Fixes (Priority Order)

1. **Fix Organization tab session crash**: The `ByokKeyManagementCard` keysQuery should either:
   - Be gated to enterprise tier in its `enabled` condition
   - Have its error handled gracefully (wrap in try/catch returning empty array)
   - Or the `isSessionExpiredError` logic should be updated to not treat "Invalid API key" as session expiry

2. **Fix Organization Admin page race condition**: Add a guard in the redirect useEffect to wait for orgId to be populated before checking admin status. Something like:
   ```
   if (roleLoading || orgLoading || !orgId) return;
   ```

3. **Support all tab query params in settings page**: Extend the useEffect to handle all valid tab values, not just `billing`.

4. **Clarify webhook tier gating**: Either add enterprise gate or confirm it's intentionally available to all tiers.
