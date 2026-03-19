# TEAM_258 -- Stripe Connect Payout Wiring

## Status: Complete

## Changes Made

### Backend: services/billing-service/app/api/v1/endpoints.py
- Added `POST /billing/connect/onboarding` endpoint
- Creates/finds Stripe Connect account for the org, then generates an onboarding link
- Uses existing `StripeService.create_connect_account()` and `create_connect_onboarding_link()`
- Return/refresh URLs point back to `/billing` with `?connect_return=true` / `?connect_refresh=true`

### Dashboard API client: apps/dashboard/src/lib/api.ts
- Added `ConnectOnboardingResponse` interface
- Added `createConnectOnboardingLink(accessToken)` method

### Dashboard UI: apps/dashboard/src/app/billing/page.tsx
- Added `connectOnboardingMutation` using react-query
- Replaced hardcoded disabled "Coming Soon" button with live "Connect Payout Account" button
- Shows "Payout Account Connected" badge with checkmark when `coalition.payout_account_connected` is true
- Handles `?connect_return=true` search param with success toast
- Handles `?connect_refresh=true` search param with info toast about incomplete onboarding

## Build Verification
- TypeScript: zero type errors in modified files (billing/page.tsx, api.ts)
- Python: syntax valid
- Note: `next build` fails due to pre-existing type error in api-keys/page.tsx from another agent (TEAM_257 IP allowlisting), not from these changes

## Suggested Commit Message
```
feat: wire Stripe Connect payout onboarding end-to-end

- Add POST /billing/connect/onboarding endpoint to billing-service
- Add createConnectOnboardingLink() to dashboard API client
- Replace disabled "Coming Soon" button with live Connect flow
- Show "Payout Account Connected" badge when connected
- Handle connect_return and connect_refresh URL params with toasts
```
