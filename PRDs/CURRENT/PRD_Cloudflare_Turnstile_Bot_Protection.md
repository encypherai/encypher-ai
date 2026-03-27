# PRD: Cloudflare Turnstile Bot Protection

## Status: COMPLETE
## Current Goal: Deploy -- requires Cloudflare Turnstile keys in Railway env vars

## Overview
Integrate Cloudflare Turnstile (managed mode) across all public-facing forms on marketing-site and dashboard to block bot spam while preserving UX for real users. Server-side token validation happens in the Next.js API layer.

## Objectives
- Block automated form submissions (bot spam, credential stuffing)
- Maintain frictionless UX for legitimate users (managed mode -- invisible unless suspicious)
- Validate tokens server-side before processing any form submission
- Graceful degradation if Turnstile fails to load

## Tasks

### 1.0 Infrastructure
- [x] 1.1 Install @marsidev/react-turnstile in marketing-site -- build clean
- [x] 1.2 Install @marsidev/react-turnstile in dashboard -- build clean
- [x] 1.3 Create TurnstileWidget component (marketing-site)
- [x] 1.4 Create verifyTurnstileToken server utility (marketing-site)
- [x] 1.5 Create TurnstileWidget component (dashboard)
- [x] 1.6 Create verifyTurnstileToken server utility (dashboard)

### 2.0 Marketing Site -- Forms
- [x] 2.1 Contact page form (/contact/page.tsx)
- [x] 2.2 Demo request page form (/demo/page.tsx)
- [x] 2.3 AI Demo DemoRequestModal
- [x] 2.4 Publisher Demo DemoRequestModal
- [x] 2.5 SalesContactModal (all 4 contexts)
- [x] 2.6 BlogNewsletter component
- [N/A] 2.7 SignInForm -- marketing site auth forms delegate to dashboard
- [N/A] 2.8 SignUpForm -- marketing site auth forms delegate to dashboard

### 3.0 Marketing Site -- Server Validation
- [x] 3.1 /api/demo-request route -- validate before proxying
- [x] 3.2 /api/newsletter/subscribe route -- validate before proxying

### 4.0 Dashboard -- Public Forms
- [x] 4.1 Login page (/login) -- Turnstile widget + token passed through NextAuth
- [x] 4.2 Signup page (/signup) -- redirected through proxy API route
- [x] 4.3 Forgot password page (/forgot-password) -- redirected through proxy API route
- [SKIP] 4.4 Reset password page -- already gated by single-use token
- [SKIP] 4.5 Team invite accept -- already gated by invitation token
- [SKIP] 4.6 Org invite accept -- already gated by invitation token

### 5.0 Dashboard -- Server Validation
- [x] 5.1 NextAuth authorize -- validate turnstile token for credential logins
- [x] 5.2 Create /api/auth/signup proxy route with validation
- [x] 5.3 Create /api/auth/forgot-password proxy route with validation
- [SKIP] 5.4 Reset password -- already token-gated
- [SKIP] 5.5 Accept invite -- already token-gated

### 6.0 Configuration and Testing
- [x] 6.1 Env vars documented below
- [x] 6.2 Build marketing-site -- clean
- [x] 6.3 Build dashboard -- clean

## Deployment: Required Environment Variables

Set these in Railway for both **marketing-site** and **dashboard** services:

| Variable | Scope | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_TURNSTILE_SITE_KEY` | Client | Cloudflare Turnstile site key (visible in browser) |
| `TURNSTILE_SECRET_KEY` | Server | Cloudflare Turnstile secret key (never exposed to client) |

### How to get Turnstile keys:
1. Log in to Cloudflare dashboard
2. Go to Turnstile (left sidebar)
3. Click "Add site"
4. Set domain to `encypher.com` (add `localhost` for dev)
5. Widget type: "Managed" (recommended)
6. Copy Site Key and Secret Key

### Dev mode behavior:
- If `TURNSTILE_SECRET_KEY` is not set and `NODE_ENV=development`: server-side verification is skipped
- If `NEXT_PUBLIC_TURNSTILE_SITE_KEY` is not set: widget renders nothing (forms work without it)
- In production: both keys are required; missing secret key returns 403 on form submissions

## Success Criteria
- [x] All public forms require valid Turnstile token before submission
- [x] Server-side validation rejects requests without valid tokens
- [x] Forms degrade gracefully if Turnstile script fails to load
- [x] No visible impact on legitimate user experience (managed mode = invisible for most users)
- [x] Both apps build clean

## Completion Notes
- Protected 9 form surfaces: 6 marketing-site forms + 3 dashboard auth forms
- Reset-password, team-invite, and org-invite pages skipped (already gated by single-use tokens)
- Turnstile tokens reset automatically on form submission failure (forces re-verification)
- Submit buttons disabled until Turnstile verification completes
