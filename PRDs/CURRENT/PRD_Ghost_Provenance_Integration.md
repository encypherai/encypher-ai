# PRD: Ghost CMS Provenance Integration

**Status:** Phase 1 Implementation Complete  
**Current Goal:** Core integration service built, tested, and ready for local Docker testing  
**Team:** TEAM_183

## Overview

Ghost CMS (https://ghost.org/) is a popular open-source Node.js headless CMS used by publishers, newsletters, and content creators. Unlike WordPress, Ghost has **no native plugin system** — it relies on webhooks, an Admin API, and themes for extensibility. This PRD proposes building an external Node.js microservice that listens for Ghost webhooks and uses the Ghost Admin API + Encypher Enterprise API to automatically sign published content with C2PA-compliant invisible embeddings, plus a theme helper for front-end verification badges.

## Objectives

- Provide Ghost publishers with automatic C2PA provenance signing on publish/update, matching the WordPress plugin's core value proposition
- Build a standalone Node.js integration service that connects Ghost webhooks → Encypher Enterprise API → Ghost Admin API
- Support the same tier model (Free / Pro / Enterprise) as the WordPress plugin
- Provide a front-end verification badge for readers via Ghost theme injection or code injection
- Include a companion configuration UI (lightweight web dashboard) since Ghost has no editor plugin extension points
- Ship with Docker Compose for easy local development and deployment

## Architecture

### WordPress Plugin (reference)

The WordPress plugin runs **inside** WordPress as a PHP plugin. It hooks into `publish_post`/`post_updated` actions, exposes WP REST endpoints, provides a Gutenberg sidebar panel, stores metadata in post meta fields, and renders verification badges via theme hooks.

### Ghost Integration (proposed)

The Ghost integration runs as an **external Node.js microservice**. Ghost has no internal plugin API, so the integration pattern is:

```
Ghost CMS ──webhook──► Encypher Ghost Service ──sign──► Enterprise API
    ▲                         │
    └──Admin API (update)─────┘
```

**Key components:**

1. **Webhook Receiver** — Express.js server listening for Ghost webhook events
2. **Ghost Admin API Client** — Uses `@tryghost/admin-api` to read/write posts
3. **Encypher API Client** — Calls Enterprise API `/api/v1/sign` and `/api/v1/verify`
4. **Loop Prevention** — Tracks in-flight signing operations to avoid infinite webhook loops
5. **Config Dashboard** — Lightweight web UI for managing API keys, settings, and viewing signing status
6. **Theme Helper / Code Injection** — JavaScript snippet for front-end verification badges

### Webhook Events Used

| Ghost Event | Maps To | Action |
|-------------|---------|--------|
| `post.published` | New post published | Sign with `c2pa.created` |
| `post.published.edited` | Published post updated | Sign with `c2pa.edited` |
| `page.published` | New page published | Sign with `c2pa.created` |
| `page.published.edited` | Published page updated | Sign with `c2pa.edited` |

### Data Flow (Auto-Sign on Publish)

1. Author publishes/updates post in Ghost Admin editor
2. Ghost fires `post.published` or `post.published.edited` webhook to integration service
3. Service checks loop-prevention cache — skip if already processing this post
4. Service adds post ID to in-flight set
5. Service calls Ghost Admin API: `GET /ghost/api/admin/posts/{id}/?formats=html`
6. Service extracts plain text from HTML, builds signing request with metadata (title, author, published_at, URL, ghost_post_id)
7. Service calls Encypher Enterprise API: `POST /api/v1/sign`
8. Enterprise API returns `embedded_content` with invisible C2PA manifests
9. Service calls Ghost Admin API: `PUT /ghost/api/admin/posts/{id}/` with signed HTML and current `updated_at`
10. Service records signing metadata (document_id, merkle_root, timestamp) in local SQLite/JSON store
11. Service removes post ID from in-flight set
12. Optionally updates post's `codeinjection_foot` with verification badge script

### Metadata Storage

Ghost posts lack arbitrary meta fields. Strategy:

- **Internal tags**: Apply `#encypher-signed` tag to signed posts (filterable in Ghost Admin)
- **Local database**: SQLite file mapping `ghost_post_id → {document_id, merkle_root, signed_at, content_hash, action_type}`
- **Code injection**: Store minimal JSON in `codeinjection_head` for front-end badge to read

### Front-End Verification Badge

Two options (both supported):

1. **Code Injection** (zero theme changes): Service writes a `<script>` tag into the post's `codeinjection_foot` that renders a verification badge and calls the public verify endpoint
2. **Theme Partial** (for custom themes): Provide a Handlebars partial (`partials/encypher-badge.hbs`) that theme developers can include in `post.hbs`

## Feature Parity Matrix

| Feature | WordPress Plugin | Ghost Integration |
|---------|-----------------|-------------------|
| Auto-sign on publish | ✅ Hook-based | ✅ Webhook-based |
| Auto-sign on update | ✅ Hook-based | ✅ Webhook-based |
| Manual sign from editor | ✅ Gutenberg sidebar | ❌ Not possible (no editor plugin API) |
| Manual sign from dashboard | ❌ N/A | ✅ Companion config UI |
| Verification badge (front-end) | ✅ Theme hook | ✅ Code injection + theme partial |
| Provenance chain (edit history) | ✅ Ingredient references | ✅ Same via Enterprise API |
| Bulk signing of archives | ✅ Admin page | ✅ Config dashboard page |
| Settings UI | ✅ WP Admin page | ✅ Companion config dashboard |
| Tier support (Free/Pro/Enterprise) | ✅ | ✅ |
| Whitelabeling | ✅ Pro/Enterprise | ✅ Pro/Enterprise |
| Content hash caching (no double-sign) | ✅ Post meta | ✅ Local SQLite |

## Project Structure

```
integrations/ghost-provenance/
├── README.md
├── package.json
├── tsconfig.json
├── docker-compose.yml          # Ghost + Integration Service + Enterprise API
├── Dockerfile
├── .env.example
├── src/
│   ├── index.ts                # Express app entry point
│   ├── config.ts               # Environment config (Ghost URL, API keys, Encypher keys)
│   ├── ghost-client.ts         # Ghost Admin API wrapper
│   ├── encypher-client.ts      # Encypher Enterprise API client
│   ├── webhook-handler.ts      # Webhook receiver + loop prevention
│   ├── signer.ts               # Orchestrates read → sign → write-back flow
│   ├── metadata-store.ts       # SQLite store for signing metadata
│   ├── badge-injector.ts       # Generates verification badge code injection
│   ├── html-utils.ts           # HTML → plain text extraction
│   └── dashboard/              # Lightweight config UI (optional, could be separate)
│       ├── server.ts
│       └── views/
├── theme-helpers/
│   └── partials/
│       └── encypher-badge.hbs  # Handlebars partial for Ghost themes
├── tests/
│   ├── webhook-handler.test.ts
│   ├── signer.test.ts
│   ├── ghost-client.test.ts
│   ├── encypher-client.test.ts
│   └── html-utils.test.ts
└── docs/
    ├── SETUP.md
    └── ARCHITECTURE.md
```

## Tasks

### 1.0 Project Setup
- [x] 1.1 Initialize Node.js/TypeScript project with package.json, tsconfig — ✅ vitest
- [x] 1.2 Add dependencies: `@tryghost/admin-api`, `express`, `better-sqlite3`, `jsonwebtoken`, `node-html-parser` — ✅ npm install
- [x] 1.3 Create `.env.example` with all config variables
- [x] 1.4 Create `docker-compose.yml` (Ghost + MySQL + Integration Service + Enterprise API + PostgreSQL)
- [x] 1.5 Create Dockerfile for integration service

### 2.0 Core Integration Service
- [x] 2.1 Implement `config.ts` — env-based configuration — ✅ vitest
- [x] 2.2 Implement `ghost-client.ts` — Ghost Admin API wrapper (read post, update post, add tag) — ✅ vitest
- [x] 2.3 Implement `encypher-client.ts` — Enterprise API client (sign, verify) — ✅ vitest
- [x] 2.4 Implement `html-utils.ts` — HTML to plain text extraction with Ghost card handling — ✅ vitest (45 tests)
- [x] 2.5 Implement `metadata-store.ts` — SQLite store for signing records — ✅ vitest
- [x] 2.6 Implement `webhook-handler.ts` — Express routes for Ghost webhooks with loop prevention — ✅ vitest (11 tests)
- [x] 2.7 Implement `signer.ts` — Orchestration: read → sign → write-back → record — ✅ vitest
- [x] 2.8 Implement `badge-injector.ts` — Code injection for verification badge — ✅ vitest
- [x] 2.9 Implement `index.ts` — Express app bootstrap — ✅ tsc build clean

### 3.0 Front-End Verification
- [x] 3.1 Create verification badge JavaScript snippet (for code injection)
- [x] 3.2 Create Handlebars theme partial (`encypher-badge.hbs`)
- [ ] 3.3 Badge calls public verify endpoint and renders result (Phase 2 — badge currently links to verify URL)

### 4.0 Testing
- [x] 4.1 Unit tests for `html-utils.ts` — ✅ 45 tests passing
- [x] 4.2 Unit tests for `webhook-handler.ts` (including loop prevention) — ✅ 11 tests passing
- [ ] 4.3 Unit tests for `signer.ts` (mocked Ghost + Encypher clients) — Phase 2
- [ ] 4.4 Integration tests with Docker Compose stack — Phase 2
- [x] 4.5 Manual end-to-end test: publish post in Ghost → verify signed content — ✅ 2022 VS chars embedded, #encypher-signed tag added, badge injected

### 5.0 Documentation
- [x] 5.1 README with setup instructions
- [x] 5.2 Architecture documented in README
- [x] 5.3 Ghost Admin setup guide (creating custom integration, configuring webhooks)

### 6.0 Config Dashboard (Phase 2)
- [ ] 6.1 Lightweight web UI for API key configuration
- [ ] 6.2 Signing status/history view
- [ ] 6.3 Bulk sign existing posts
- [ ] 6.4 Per-post override (skip signing)

## Success Criteria

- [x] Ghost webhook `post.published` triggers automatic C2PA signing of post content
- [x] Ghost webhook `post.published.edited` triggers re-signing with `c2pa.edited` action
- [x] Signed content is written back to Ghost post via Admin API
- [x] No infinite webhook loops — ✅ in-flight lock mechanism verified
- [x] Verification badge renders on published posts — ✅ codeinjection_foot injected (1302 chars)
- [x] All unit tests pass — ✅ 56 tests passing
- [x] Docker Compose stack runs Ghost + Integration Service + Enterprise API together — ✅ verified
- [x] README provides clear setup instructions for both self-hosted and Ghost(Pro) users

## Completion Notes

**Phase 1 complete (2026-02-13).** Core integration service built with 56 passing tests and clean TypeScript build. All source modules, Docker Compose stack, Dockerfile, and documentation created.

**E2E verified (2026-02-13).** Full signing flow tested: Ghost webhook → read post → extract text (234 chars) → Enterprise API /sign → embed signed text (2022 VS chars) → update Ghost post (4331 bytes HTML) → add #encypher-signed tag → inject verification badge. Docker networking resolved via shared `encypher-network` to reach Enterprise API container directly.

**Regression hardening (2026-02-17, TEAM_206).** Fixed HTML re-embedding alignment when Ghost HTML contains named/numeric entities (e.g., `&mdash;`, `&#8212;`) so sentence-level markers are preserved in the correct segment positions. Added tests asserting `manifest_mode=micro_ecc_c2pa` + `segmentation_level=sentence` are forwarded and entity-heavy HTML keeps per-sentence markers intact. ✅ `npm test` (63/63)

**Embedding-plan insertion upgrade (2026-02-17, TEAM_206).** Added a primary signer path that applies `embedding_plan` `codepoint` operations directly into original HTML text nodes via byte-offset insertion, reducing reliance on signed-text round-tripping. Added regression tests for cross-paragraph insertion, `insert_after_index=-1`, and plan bounds validation; signer retains reconstructed/returned `signed_text` as fallback. ✅ `npm test` (66/66)
