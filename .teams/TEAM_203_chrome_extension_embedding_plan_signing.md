# TEAM_203 — Chrome Extension Cross-System Signing + Verification Hardening

## Session Summary
Implemented a broader hardening pass for the Chrome extension across both signing and verification workflows:
- embedding-plan-aware signing fallback
- verification dedupe/retry architecture
- richer revoked/mixed verification UX in popup + icon states

## Scope Completed
- Added request helper to force `return_embedding_plan=true` for sign requests.
- Added embedding-plan reconstruction utility for codepoint-index marker insertion.
- Added signed-text resolver with priority order:
  1. `signed_text`
  2. `embedded_content`
  3. `embedding_plan` reconstruction
- Wired service-worker signing to use new resolver and return explicit error when neither direct output nor valid plan is available.
- Added verification helper module with:
  - transient retry classification (`shouldRetryVerification`)
  - deterministic tab-state transitions (verified/invalid/revoked/pending)
  - bounded detail-list append behavior
  - icon state resolution including `revoked` and `mixed`
- Updated service-worker verification flow to:
  - dedupe in-flight identical verify requests
  - retry once for transient failures
  - persist richer per-tab verification details for popup
  - surface revoked/mixed icon badges
- Updated popup verify UX to:
  - show revoked counter
  - render marker type + status metadata for each verification detail
- Implemented DOM-preserving embedding-plan insertion in `editor-signer` for contenteditable selections by mapping codepoint operations to range text-node offsets with alignment guards and fallback replacement.
- Extended DOM-preserving insertion with an online-editor-specific fallback path for Google Docs / Office Online edge cases where browser selection/range behavior is non-standard.
- Hardened online-editor fallback with whitespace normalization matching (NBSP/newline/tab collapse) before exact matching, to tolerate Docs/Office segmentation drift.
- Added dedicated journey documentation for Reader/Verifier and Publisher/Creator, including privacy posture, network effect framing, and verification matrix.
- Aligned popup Verify UX more closely to journey requirements with a signed-content headline, frictionless sign CTA, and per-item verification links.
- Hardened context-menu verification/signing flow by carrying page metadata for right-click verify actions and adding explicit context-menu test coverage.
- Fixed right-click sign/verify behavior in iframe-based editors by routing context-menu actions to the originating frame (`frameId`) instead of only top frame.
- Enabled content-script coverage for WYSIWYG iframe panes via manifest `all_frames` + `match_about_blank`.
- Added localhost/127.0.0.1 host permissions so local superadmin API keys work with local API base URLs.
- Surfaced signer identity (publisher display name fallback to organization) in both popup sign state and extension settings.
- Added dedicated tests for both signing and verification helper behavior plus popup UX assertions.

## Files Changed
- `integrations/chrome-extension/background/service-worker.js`
- `integrations/chrome-extension/background/signing-utils.js` (new)
- `integrations/chrome-extension/background/verification-utils.js` (new)
- `integrations/chrome-extension/popup/popup.html`
- `integrations/chrome-extension/popup/popup.js`
- `integrations/chrome-extension/popup/popup.css`
- `integrations/chrome-extension/options/options.html`
- `integrations/chrome-extension/options/options.js`
- `integrations/chrome-extension/options/options.css`
- `integrations/chrome-extension/content/editor-signer.js`
- `integrations/chrome-extension/manifest.json`
- `integrations/chrome-extension/tests/signing-utils.test.js` (new)
- `integrations/chrome-extension/tests/verification-utils.test.js` (new)
- `integrations/chrome-extension/tests/popup-verification-ux.test.js` (new)
- `integrations/chrome-extension/tests/editor-signer-embedding-plan.test.js` (new)
- `integrations/chrome-extension/USER_JOURNEYS.md` (new)
- `integrations/chrome-extension/README.md`
- `integrations/chrome-extension/tests/context-menu-flow.test.js` (new)

## Validation
- ✅ `node --test tests/signing-utils.test.js`
- ✅ `node --test tests/verification-utils.test.js tests/popup-verification-ux.test.js tests/signing-utils.test.js`
- ✅ `node --test tests/editor-signer-embedding-plan.test.js`
- ✅ `npm test`
- ✅ `npm run lint`
- ✅ `npm run test:e2e`

## Notes / Risks
- DOM-preserving insertion now covers contenteditable selections when selected visible text aligns with embedding plan operations.
- Online-editor fallback now attempts unique-match insertion inside Google Docs / Office Online editor roots when direct selection-range insertion is not viable.
- Online-editor fallback now first attempts normalized unique matching (NBSP/newline drift tolerant), then exact unique matching, before fallback replacement.
- Fallback paths remain in place (full signed-text replacement, then clipboard) for non-aligning ranges, non-unique matches, and non-editable contexts.

## Handoff
Next improvement (if desired): expand DOM-preserving insertion to additional editor-specific models (e.g., richer Google Docs/Office editable surfaces where browser range behavior is non-standard).

## Suggested Commit Message
feat(chrome-extension): fix iframe context-menu signing and show publisher identity

- add background/signing-utils.js with:
  - withEmbeddingPlanRequest() to enforce return_embedding_plan=true
  - applyEmbeddingPlanToText() for codepoint-index marker insertion
  - resolveSignedText() to prioritize signed_text, then embedded_content, then embedding_plan
- add background/verification-utils.js with:
  - shouldRetryVerification() for transient retry decisions
  - buildVerificationDetail()/appendVerificationDetail() for bounded detail history
  - updateTabStateWithVerification()/getIconStateForTab() for deterministic verification state
- update background/service-worker.js flows to:
  - include return_embedding_plan in options
  - resolve signed text via utility fallback
  - return explicit error when response has no valid signed output
  - include embeddingPlan in success payload
- dedupe concurrent verify calls and retry transient failures once
- persist detail metadata (marker type/status/date/signer) for popup rendering
- expose revoked/mixed icon states
- update popup verify UI to include revoked count and detail metadata row
- add DOM-preserving embedding-plan insertion in content/editor-signer.js:
  - normalize and validate embedding-plan operations
  - map codepoint insertion offsets to selected text-node UTF-16 offsets
  - mutate nodes in-place with visible-text alignment guard
  - add Google Docs / Office Online fallback that applies operations against unique visible-text matches in editor roots
  - add whitespace normalization helpers for Google Docs/Office text segmentation drift
  - fallback to signed_text replacement when plan application is unsafe
- add tests/signing-utils.test.js, verification-utils.test.js, popup-verification-ux.test.js, editor-signer-embedding-plan.test.js covering:
  - option enrichment with return_embedding_plan
  - plan reconstruction success/failure paths
  - signed-text resolution priority and null fallback
  - verification retry/state/icon/detail behaviors
  - popup revoked counter + marker/status detail rendering
  - editor-signer embedding-plan application and fallback ordering
- add USER_JOURNEYS.md with:
  - Reader/Verifier and Publisher/Creator end-to-end flows
  - privacy and discovery-tracking model aligned with extension behavior
  - convergence/network effect narrative and current verification matrix
- update README.md to link journey documentation
- enhance popup verify UX with:
  - explicit "Signed content detected on this page" headline
  - low-friction verify-tab CTA to jump into Sign flow
  - detail-level "View verification" links using verification_url/document_id
- wire right-click verify metadata through context menu + detector path:
  - include pageUrl/pageTitle in VERIFY_SELECTION dispatch
  - preserve marker/page context when forwarding to VERIFY_CONTENT
- route right-click verify/sign to originating iframe using `info.frameId` to fix selected-text signing in WYSIWYG surfaces
- expand manifest coverage for editor panes:
  - `all_frames: true`
  - `match_about_blank: true`
- allow local API base URLs used by superadmin/local testing:
  - `http://localhost/*`
  - `http://127.0.0.1/*`
- add signer identity UX:
  - popup sign tab shows `Signing as: <publisher display name | org name>`
  - options page shows the same identity after API key validation/load
  - service worker account info includes `publisherDisplayName` and `anonymousPublisher`
- include verification_url in service-worker verify payload mapping for popup detail links
- extend tests/context-menu-flow.test.js for iframe frame targeting + manifest frame coverage
- extend tests/onboarding-setup-flow.test.js for signer identity UI + localhost host permission coverage
- verify with npm test + npm run lint + npm run test:e2e

## Latest Regression Fix Pass (Localhost + Identity + Context Menu)
- Normalized account payload parsing for both wrapped (`{ success, data }`) and flat responses in extension settings and service-worker account lookups.
- Fixed "Connected as undefined" by resolving organization identity from `organization_name || name || organization.name`.
- Added account identity fields to Enterprise API `/api/v1/account` response:
  - `publisher_display_name`
  - `anonymous_publisher`
- Hardened right-click sign/verify actions with frame-aware fallback delivery:
  - retries message delivery across requested frame then top frame
  - attempts explicit content-script injection (`detector.js`, `editor-signer.js`) on recoverable messaging failures
  - shows immediate in-page UX feedback (`Signing selected text...`) and actionable error toasts on failure
- Improved detector runtime messaging resilience:
  - classify disconnect/port errors
  - retry once for transient service-worker restart races before surfacing "Extension disconnected"
  - use safe messaging path for selected-text verification notifications

### Additional Files Updated
- `enterprise_api/app/routers/account.py`
- `enterprise_api/tests/test_account.py`

### Additional Validation
- ✅ `node --test tests/context-menu-flow.test.js`
- ✅ `node --test tests/onboarding-setup-flow.test.js`
- ✅ `node --test tests/detector.test.js`
- ✅ `uv run pytest tests/test_account.py`

## Updated Suggested Commit Message
fix(chrome-extension): resolve localhost signing regressions and identity mapping gaps

- normalize account parsing across extension settings/background for wrapped `success/data` and flat payloads
- fix settings identity label by falling back to `organization_name || name || organization.name`
- include publisher identity fields in enterprise `/api/v1/account` response (`publisher_display_name`, `anonymous_publisher`)
- harden context-menu selected-text sign/verify delivery:
  - send to originating frame with fallback to top frame
  - inject content scripts on recoverable "no receiver" errors
  - show immediate in-page toasts for sign-start and actionable failures
- improve detector messaging resilience to reduce false "Extension disconnected" badges by retrying transient runtime disconnect races
- add/extend regression tests for:
  - context-menu fallback + frame targeting
  - wrapped account payload parsing
  - localhost host permissions
  - account endpoint publisher identity fields
- validate with:
  - npm test
  - npm run lint
  - npm run test:e2e
  - uv run pytest tests/test_account.py

## Follow-up: WYSIWYG In-Place Signing + Badge Pollution Regression
- Root cause: detector injected inline `.encypher-badge` nodes into editable content blocks, which polluted underlying HTML/source panes and caused conflicting badge states (invalid + verified siblings).
- Fix: render badges as floating body-level overlays for editable surfaces (`contenteditable`, textarea/input) while keeping inline badges for static/non-editable page content.
- Preserve editor content integrity by avoiding `element.appendChild(badge)` and `encypher-verified-content` class mutations on editable targets.
- Added regression assertions in popup branding/debug suite for editable-surface floating badge behavior.

### Validation (follow-up)
- ✅ `node --test tests/popup-branding-and-debug.test.js`
- ✅ `node --test tests/detector.test.js`
- ✅ `npm test`
- ✅ `npm run lint`
- ✅ `npm run test:e2e`

### Commit message addon
- fix(detector): keep verification badges out of editable HTML by floating overlays
  - add editable-surface detection + floating badge placement
  - prevent inline badge/class mutations inside WYSIWYG/editor content
  - add regression test for non-intrusive badge rendering in editable contexts

## Follow-up: Sign Tab Auth Onboarding + Dashboard Redirect UX
- Goal: make the no-key sign state production-ready by guiding users through the same auth methods available in Dashboard, then syncing credentials directly in popup.
- Implemented in popup Sign no-key state:
  - dashboard login/signup CTAs
  - social/passkey quick actions (Google, GitHub, Passkey)
  - guided setup copy for creating signing identity + API key in dashboard
  - quick API key sync input + validation/save path in popup
- Implemented in service worker:
  - dashboard auth URL derivation from API base URL (`api.* -> dashboard.*`, localhost fallback)
  - `OPEN_DASHBOARD_AUTH` message handler that opens dashboard auth routes in a new tab
- Preserved prior onboarding path:
  - optional email auto-provisioning (`AUTO_PROVISION_EXTENSION_USER`) remains available as instant setup

### Files updated (this follow-up)
- `integrations/chrome-extension/popup/popup.html`
- `integrations/chrome-extension/popup/popup.css`
- `integrations/chrome-extension/popup/popup.js`
- `integrations/chrome-extension/background/service-worker.js`
- `integrations/chrome-extension/tests/onboarding-setup-flow.test.js`

### Validation (this follow-up)
- ✅ `node --test tests/onboarding-setup-flow.test.js`
- ✅ `node --test tests/popup-verification-ux.test.js`
- ✅ `npm run lint`
- ✅ `npm test`
- ✅ `npm run test:e2e`

### Suggested commit message (comprehensive)
feat(chrome-extension): add dashboard-auth onboarding flow and in-popup credential sync for sign tab

- revamp popup sign no-key UX with guided setup flow:
  - add dashboard login and signup CTAs
  - add Google/GitHub/Passkey quick auth actions
  - add setup guidance for signing identity + dashboard API key creation
  - add quick API key sync input/button in popup
- implement popup handlers:
  - `openDashboardAuth(mode, provider)` to launch dashboard auth through background worker
  - `saveQuickApiKey()` to validate account access, persist key, mark setup complete, and transition to sign-ready state
- extend background/service-worker:
  - add `dashboardBaseUrl` config and derivation from API base URL
  - add `buildDashboardAuthUrl()` helper with extension-source metadata
  - add `OPEN_DASHBOARD_AUTH` runtime message handler using `chrome.tabs.create`
  - keep dashboard URL derivation in sync when API base URL changes
- preserve and complement existing email auto-provision setup path
- add regression coverage to onboarding tests for:
  - new popup auth CTA elements
  - dashboard auth wiring in popup JS
  - service-worker dashboard auth open handler
- verify with lint, full unit tests, and e2e suite

## Follow-up: Dashboard Callback Handoff (3-5 Click Onboarding Path)
- Goal: remove manual API-key copy/paste for most users by handing off newly generated keys from dashboard to extension via trusted external runtime messaging.

### Implemented
- Extension manifest external messaging allowlist:
  - added `externally_connectable.matches` for dashboard + localhost origins so dashboard pages can message the extension directly.
- Extension service worker hardening:
  - `buildDashboardAuthUrl()` now includes a `callbackUrl` to `/extension-handoff` with `source` + `extensionId` metadata.
  - added `isTrustedExternalSender()` origin validation.
  - added `handleDashboardApiKeyHandoff()` for `DASHBOARD_API_KEY_HANDOFF` external messages:
    - validates sender origin
    - validates API key format
    - validates key against `/api/v1/account`
    - persists API key and onboarding state (`onboardingSource: dashboard_handoff`)
    - warms account identity cache for immediate sign-tab readiness
  - added `chrome.runtime.onMessageExternal` listener for dashboard handoff.
- Dashboard auth flow propagation:
  - login page reads extension handoff query params (`source`, `extensionId`, `callbackUrl`, `provider`) via `useSearchParams`.
  - login OAuth/credentials/passkey sign-in now preserves `callbackUrl`.
  - login page auto-starts Google/GitHub auth when `provider` is present.
  - signup page propagates callback metadata through OAuth buttons and login links.
- New dashboard route:
  - added `/extension-handoff` page that creates an API key and attempts direct extension sync with `chrome.runtime.sendMessage(extensionId, { type: 'DASHBOARD_API_KEY_HANDOFF', apiKey })`.
  - includes manual copy fallback UX when runtime messaging is unavailable.

### Files updated (callback handoff follow-up)
- `integrations/chrome-extension/manifest.json`
- `integrations/chrome-extension/background/service-worker.js`
- `integrations/chrome-extension/tests/onboarding-setup-flow.test.js`
- `apps/dashboard/src/app/login/page.tsx`
- `apps/dashboard/src/app/signup/page.tsx`
- `apps/dashboard/src/app/extension-handoff/page.tsx` (new)

### Validation (callback handoff follow-up)
- ✅ `node --test tests/onboarding-setup-flow.test.js`
- ✅ `npm test` (chrome extension)
- ✅ `npm run lint` (chrome extension)
- ✅ `npm run type-check` (dashboard)
- ✅ `npm run lint` (dashboard; existing non-blocking warnings remain)
- ⏹️ `npm run test:e2e` (chrome extension/dashboard) attempted but canceled in IDE

### Updated Suggested Commit Message (comprehensive)
feat(onboarding): add dashboard callback handoff for one-step extension credential sync

- add external runtime allowlist in extension manifest (`externally_connectable.matches`) for dashboard + local dev origins
- extend service-worker dashboard auth URL builder with callback metadata (`callbackUrl=/extension-handoff`, `source`, `extensionId`, optional `provider`)
- add secure external handoff path in service-worker:
  - trust-check sender origins before accepting external messages
  - accept `DASHBOARD_API_KEY_HANDOFF` messages from dashboard pages
  - validate handed-off API key via `/api/v1/account`
  - persist key + onboarding completion (`onboardingSource=dashboard_handoff`)
  - prefill account identity cache for immediate sign-tab readiness
- update dashboard login/signup pages to preserve extension callback context across credentials + OAuth
- auto-trigger Google/GitHub auth when dashboard login is opened with `provider` from extension
- add new dashboard route `/extension-handoff` to:
  - generate a fresh API key
  - post it to extension with `chrome.runtime.sendMessage`
  - present copy fallback when runtime handoff is unavailable
- add regression tests covering:
  - manifest external connect policy
  - service-worker external handoff handler + callback URL wiring
  - dashboard auth/query propagation and handoff-page message contract
- validate with extension unit suite, extension lint, dashboard type-check, and dashboard lint
