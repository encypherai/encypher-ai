# TEAM_282 -- Cloudflare Turnstile Bot Protection

## Status: COMPLETE

## Summary
Integrated Cloudflare Turnstile across marketing-site and dashboard to protect all public-facing forms from bot spam. Both apps build clean.

## What was done

### Infrastructure (both apps)
- Installed `@marsidev/react-turnstile` package
- Created `TurnstileWidget` component (managed mode, auto theme, flexible size)
- Created `verifyTurnstileToken()` server-side utility with dev-mode bypass

### Marketing Site (6 forms, 2 API routes)
- Contact page form
- Demo request page form
- AI Demo DemoRequestModal
- Publisher Demo DemoRequestModal
- SalesContactModal (all 4 contexts: ai, publisher, enterprise, general)
- BlogNewsletter component
- `/api/demo-request` route -- server-side validation before proxy
- `/api/newsletter/subscribe` route -- server-side validation before proxy

### Dashboard (3 forms, 3 server routes)
- Login page -- Turnstile widget + token passed through NextAuth credentials
- Signup page -- redirected through new `/api/auth/signup` proxy route
- Forgot password page -- redirected through new `/api/auth/forgot-password` proxy route
- NextAuth authorize callback -- validates Turnstile for credential logins
- Skipped: reset-password, team-invite, org-invite (already gated by single-use tokens)

## Files Created
- `apps/marketing-site/src/components/security/TurnstileWidget.tsx`
- `apps/marketing-site/src/lib/turnstile.ts`
- `apps/dashboard/src/components/security/TurnstileWidget.tsx`
- `apps/dashboard/src/lib/turnstile.ts`
- `apps/dashboard/src/app/api/auth/signup/route.ts`
- `apps/dashboard/src/app/api/auth/forgot-password/route.ts`

## Files Modified
- `apps/marketing-site/src/app/api/demo-request/route.ts`
- `apps/marketing-site/src/app/api/newsletter/subscribe/route.ts`
- `apps/marketing-site/src/app/contact/page.tsx`
- `apps/marketing-site/src/app/demo/page.tsx`
- `apps/marketing-site/src/app/ai-demo/components/ui/DemoRequestModal.tsx`
- `apps/marketing-site/src/app/publisher-demo/components/ui/DemoRequestModal.tsx`
- `apps/marketing-site/src/components/forms/SalesContactModal.tsx`
- `apps/marketing-site/src/components/blog/BlogNewsletter.tsx`
- `apps/dashboard/src/app/login/page.tsx`
- `apps/dashboard/src/app/signup/page.tsx`
- `apps/dashboard/src/app/forgot-password/page.tsx`
- `apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`

## Deployment Prerequisites
Set in Railway for marketing-site AND dashboard:
- `NEXT_PUBLIC_TURNSTILE_SITE_KEY` -- from Cloudflare Turnstile dashboard
- `TURNSTILE_SECRET_KEY` -- from Cloudflare Turnstile dashboard

## Suggested Commit Message
```
feat(security): integrate Cloudflare Turnstile bot protection across marketing-site and dashboard

- Add TurnstileWidget component (managed mode) and server-side verify utility to both apps
- Protect 6 marketing-site forms: contact, demo, AI demo modal, publisher demo modal,
  sales modal (4 contexts), blog newsletter
- Protect 3 dashboard auth forms: login (via NextAuth), signup, forgot-password
- Server-side validation in Next.js API layer before forwarding to backend
- Graceful dev-mode bypass when Turnstile keys not configured
- Submit buttons disabled until Turnstile verification completes
- Tokens auto-reset on submission failure for re-verification
```
