# PRD: Email Verification & Notification System

## Overview
Implement a comprehensive email system for auth-service with email verification flow, branded templates, and future CRM integration.

## Problem Statement
- Users can currently sign up and log in without email verification
- No email infrastructure exists in auth-service
- Old email templates exist but lack unified brand design
- No CRM integration for lead capture on signup

## Goals
1. **Email Verification Flow**: Require email verification before allowing login
2. **Branded Email Templates**: Modern, responsive templates matching EncypherAI brand
3. **Email Service**: Reliable email delivery via SMTP/Resend
4. **Future: Zoho CRM Integration**: Auto-add signups to CRM

---

## Task List

### 1.0 Email Infrastructure
- [x] 1.1 Create `services/auth-service/app/services/email_service.py`
  - [x] 1.1.1 SMTP configuration from env vars (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM)
  - [x] 1.1.2 Sync email sending (async can be added later)
  - [x] 1.1.3 Jinja2 template rendering
- [x] 1.2 Create email templates directory `services/auth-service/app/templates/email/`
  - [x] 1.2.1 `base.html` - Brand base template (EncypherAI colors, logo, footer)
  - [x] 1.2.2 `email_verification.html` - Verification email with CTA button
  - [x] 1.2.3 `welcome.html` - Post-verification welcome email
  - [x] 1.2.4 `password_reset.html` - Password reset email
- [ ] 1.3 Add email dependencies to `pyproject.toml` (jinja2 already included)

### 2.0 Email Verification Flow
- [x] 2.1 Database: Add `email_verification_tokens` table to core_db migration
  - [x] 2.1.1 Fields: id, user_id, token, expires_at, created_at, used, used_at
- [x] 2.2 Create verification token model in auth-service
- [x] 2.3 Update signup endpoint:
  - [x] 2.3.1 Generate verification token on signup
  - [x] 2.3.2 Send verification email
  - [x] 2.3.3 Return response indicating email sent
- [x] 2.4 Create `/auth/verify-email` endpoint
  - [x] 2.4.1 Validate token
  - [x] 2.4.2 Set `email_verified = True`, `email_verified_at = now()`
  - [x] 2.4.3 Invalidate token
  - [x] 2.4.4 Send welcome email
- [x] 2.5 Create `/auth/resend-verification` endpoint
- [x] 2.6 Update login endpoint to check `email_verified`
  - [x] 2.6.1 Return error if not verified with option to resend

### 3.0 Frontend Integration
- [x] 3.1 Marketing site: Add "Check your email" page after signup (existing in signin flow)
- [x] 3.2 Marketing site: Add email verification callback page (`/auth/verify-email`)
- [x] 3.3 Marketing site: Handle "email not verified" login error
- [x] 3.4 Marketing site: Add "Resend verification email" functionality

### 4.0 Environment Configuration
- [x] 4.1 Add env vars to auth-service config:
  - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_TLS
  - EMAIL_FROM, EMAIL_FROM_NAME
  - FRONTEND_URL (for verification links)
- [x] 4.2 Set Railway env vars for staging (partial - need SMTP_USER/SMTP_PASS)
- [x] 4.3 Document env vars in README

### 5.0 Future: Zoho CRM Integration
- [ ] 5.1 Create `services/auth-service/app/services/crm_service.py`
- [ ] 5.2 Add Zoho API credentials to config
- [ ] 5.3 On successful email verification, create/update CRM contact
- [ ] 5.4 Track signup source, tier interest, etc.

---

## Notes

### Brand Design Guidelines (for email templates)
- **Primary Color**: #1d3557 (dark blue header)
- **Accent Color**: #457b9d (CTA buttons)
- **Logo URL**: https://encypherai.com/encypher_full_nobg.png
- **Font**: Segoe UI, Arial, sans-serif
- **Max Width**: 480px container

### SMTP Options
1. **Zoho Mail** (if using Zoho CRM, good integration)
2. **Resend** (modern, good DX, generous free tier)
3. **SendGrid** (enterprise, good deliverability)
4. **AWS SES** (cheap at scale)

### Old Email Templates Reference
Located at: `c:\Users\eriks\encypher_website\backend\email_templates\`
- `base.html` - Basic brand template (needs modernization)
- `user_created.html` - Welcome email
- `invitation.html` - Org invitation
- `password_reset.html` - Password reset (placeholder)
- `security_alert.html` - Security notifications

### Token Security
- Verification tokens: 32-byte random, URL-safe base64
- Expiry: 24 hours
- Single use only
- Rate limit resend: 1 per minute

---

## Current Goal
Complete `4.3 Document env vars in README` - Final documentation

## Dependencies
- Core DB migration for `email_verification_tokens` table
- SMTP credentials (need to decide provider)

## Success Criteria
- [ ] Users receive verification email on signup
- [ ] Users cannot log in until email is verified
- [ ] Emails render correctly across major email clients
- [ ] Verification tokens expire and are single-use
