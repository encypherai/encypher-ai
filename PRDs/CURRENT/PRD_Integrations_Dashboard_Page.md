# PRD: Integrations Dashboard Page

**Status:** Implementation Complete (Phase 1 — Ghost)  
**Team:** TEAM_187  
**Created:** 2026-02-13

## Current Goal

Design and spec a unified Integrations page in the dashboard (`apps/dashboard`) that provides guided setup for all CMS integrations (Ghost, WordPress, and future ones). Each integration gets a how-to card with step-by-step instructions, credential management, and a ready-to-paste webhook URL.

## Overview

Users need a single place in the Encypher dashboard to connect their CMS platforms. The Integrations page should make setup as frictionless as possible — ideally 3 clicks and 2 pastes. It should also surface status (last webhook, sign count) and allow token regeneration without leaving the page.

## Objectives

- One page for all integrations — extensible card-based layout
- Step-by-step guided setup per integration (Ghost, WordPress, future)
- Copy-to-clipboard for webhook URLs and tokens
- Show integration status (active, last signed, sign count)
- Token regeneration with confirmation dialog
- Responsive, accessible, consistent with existing dashboard design system

## User Flow — Ghost Integration

1. User navigates to **Dashboard → Integrations**
2. Sees a card for "Ghost CMS" with a "Connect" button
3. Clicks "Connect" → modal/drawer opens with 3 steps:
   - **Step 1:** Enter Ghost URL (e.g. `https://myblog.ghost.io`)
   - **Step 2:** Enter Ghost Admin API key (with link to Ghost Admin → Integrations → Custom)
   - **Step 3:** Copy the generated webhook URL and paste it into Ghost
4. On submit, the API returns the `webhook_url` with the scoped `ghwh_` token
5. User copies the URL (one-click copy button) and pastes it into Ghost Admin → Webhooks
6. Done — card now shows "Connected" status with last webhook time and sign count

## User Flow — WordPress Integration

1. User navigates to **Dashboard → Integrations**
2. Sees a card for "WordPress" with a "Connect" button
3. Clicks "Connect" → modal/drawer with steps:
   - **Step 1:** Install the Encypher WordPress plugin (link to plugin page)
   - **Step 2:** Enter the API key from the dashboard into the plugin settings
   - **Step 3:** Configure signing preferences in the plugin
4. Card shows "Connected" once the plugin makes its first API call

## Tasks

### 1.0 Dashboard Page
- [x] 1.1 Create `/integrations` route in dashboard app
- [x] 1.2 Create `IntegrationsPage` component with card grid layout
- [x] 1.3 Integration cards: Ghost (functional), WordPress (plugin link), Substack/Medium (coming soon)

### 2.0 Ghost Integration Card
- [x] 2.1 Ghost setup wizard with 3-step flow (URL → API key → copy webhook URL)
- [x] 2.2 Form fields: Ghost URL, Admin API key with validation
- [x] 2.3 API call to `POST /api/v1/integrations/ghost`
- [x] 2.4 Display webhook URL with copy-to-clipboard button
- [x] 2.5 "Token shown once" warning banner
- [x] 2.6 Connected state: show status, last webhook, sign count, config summary
- [x] 2.7 Regenerate token with confirmation dialog
- [x] 2.8 Disconnect button with confirmation (calls `DELETE /api/v1/integrations/ghost`)

### 3.0 WordPress Integration Card
- [x] 3.1 WordPress card with "Plugin" badge and link to publisher integration guide
- [ ] 3.2 Full setup wizard (future — when plugin is ready)
- [ ] 3.3 Status display (future — when plugin reports back)

### 4.0 Shared Components
- [x] 4.1 `CopyButton` component (copies text to clipboard with visual feedback)
- [x] 4.2 Step indicator in Ghost setup wizard (numbered circles with check marks)
- [x] 4.3 Status badges (Connected/Coming Soon/Plugin)
- [x] 4.4 Cross-links: Docs page → Integrations, Integrations → Publisher Guide

### 5.0 Testing
- [x] 5.1 Dashboard build passes (`next build`)
- [x] 5.2 Enterprise API tests pass (62/62)
- [ ] 5.3 Puppeteer E2E test for Ghost integration flow (future)

## Success Criteria

- [x] User can set up Ghost integration in under 2 minutes (3-step wizard)
- [x] Webhook URL is copy-pasteable with one click (CopyButton component)
- [x] Token regeneration works with confirmation dialog
- [x] Page is responsive (grid layout adapts to screen size)
- [x] WordPress card shows plugin badge and links to setup guide
- [x] Dashboard build passes cleanly

## Design Notes

- Use existing dashboard design system (`packages/design-system`)
- Card layout: 2-column grid on desktop, single column on mobile
- Each card: integration logo/icon, name, short description, status badge, action button
- Ghost card icon: Ghost logo (or generic CMS icon)
- WordPress card icon: WordPress logo (or generic CMS icon)
- Future cards: placeholder "Coming Soon" cards for Substack, Medium, etc.
