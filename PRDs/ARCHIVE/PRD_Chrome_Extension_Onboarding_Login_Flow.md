# PRD: Chrome Extension Optional Login + Auto-Provisioned API Key

## Status: COMPLETE
## Current Goal: All tasks complete

## Overview
Add a minimal onboarding flow in the Chrome extension for new users: install, optional login, and clear value proposition. Users should be able to set up an account that auto-provisions an API key for signing while preserving manual API key override in Settings.

## Objectives
- Add optional login/setup flow in extension popup with explicit value proposition
- Auto-provision API key from onboarding flow for free users
- Persist setup state (set up vs not set up) in extension settings
- Keep manual API key entry fully supported as override path

## Tasks

### 1.0 TDD Coverage
- [x] 1.1 Add regression tests for popup onboarding UI elements and copy -- ✅ npm test
- [x] 1.2 Add regression tests for setup state tracking + provisioning message hooks -- ✅ npm test

### 2.0 Popup Onboarding UX
- [x] 2.1 Add optional login/setup UI to no-key sign state with clear benefit copy -- ✅ npm test
- [x] 2.2 Wire popup flow to call background provisioning and update local setup state -- ✅ npm test

### 3.0 Settings Tracking + Override
- [x] 3.1 Add setup tracking controls in Settings and persist setup status (manual override) -- ✅ npm test
- [x] 3.2 Ensure manual API key save updates setup state while preserving direct API key override -- ✅ npm test

### 4.0 Verification
- [x] 4.1 Unit tests pass for chrome extension -- ✅ npm test
- [x] 4.2 E2E tests pass for chrome extension -- ✅ npm run test:e2e
- [x] 4.3 Manual popup verification via Puppeteer (onboarding + setup status visibility) -- ✅ puppeteer

## Success Criteria
- Popup sign tab displays optional login/setup flow when no API key is present
- On successful setup, API key is auto-provisioned and signing is enabled without manual key entry
- Settings can explicitly mark extension set up / not set up and display setup status
- Manual API key save remains supported and can override setup path
- Tests pass and onboarding flow verified with Puppeteer

## Completion Notes
- Added optional onboarding block to Sign tab no-key state with value copy, email field, CTA, and live status messaging.
- Added popup onboarding flow that calls service-worker `AUTO_PROVISION_EXTENSION_USER` and refreshes Sign state on success.
- Added service-worker provisioning helper calling `/api/v1/provisioning/auto-provision` with extension attribution metadata and persisted setup state.
- Added settings-level setup state tracking (`extensionSetupStatus`) with explicit override control and hint messaging.
- Preserved manual API key override; successful manual save now marks setup as completed.
- Added regression suite: `tests/onboarding-setup-flow.test.js`.
- Verification completed: `npm run lint`, `npm test`, `npm run test:e2e`, and Puppeteer screenshot/manual popup inspection.
