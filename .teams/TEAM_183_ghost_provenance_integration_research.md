# TEAM_183 — Ghost CMS Provenance Integration Research

**Status:** E2E Verified  
**Started:** 2026-02-13  
**Task:** Research Ghost CMS platform and build Encypher Provenance integration similar to the WordPress plugin

## Research Findings

### Ghost CMS Architecture — Key Differences from WordPress

| Aspect | WordPress | Ghost |
|--------|-----------|-------|
| Language | PHP | Node.js |
| Plugin System | Native plugin API with hooks/filters | **No native plugin system** |
| Extension Model | Install plugins into `wp-content/plugins/` | Webhooks + Admin API + Themes |
| Editor | Gutenberg (block-based) | Lexical (JSON-based) |
| Content Format | HTML stored in DB | Lexical JSON + HTML |
| Auth for Integrations | WordPress user sessions | JWT (HS256) from Admin API keys |
| Hosting | Self-hosted or managed | Ghost(Pro) managed or self-hosted |

### Ghost Extension Mechanisms Available

1. **Custom Integrations** (Settings > Advanced > Integrations)
   - Each integration gets its own Admin API key + Content API key
   - Can configure outgoing webhooks per integration

2. **Webhooks** — Ghost fires POST requests on events:
   - `post.published` / `post.published.edited` / `post.added` / `post.edited`
   - `page.published` / `page.published.edited` / `page.added` / `page.edited`
   - `post.unpublished` / `post.deleted` / `page.unpublished` / `page.deleted`
   - `member.added` / `member.edited` / `member.deleted`
   - `site.changed`

3. **Admin API** — Full CRUD for posts/pages:
   - `GET /ghost/api/admin/posts/` — browse/read posts
   - `POST /ghost/api/admin/posts/` — create posts
   - `PUT /ghost/api/admin/posts/{id}/` — update posts (requires `updated_at`)
   - Content available in `html` and `lexical` formats
   - Auth via JWT with HS256, 5-minute expiry tokens

4. **Admin API JavaScript Client** (`@tryghost/admin-api`):
   - `api.posts.browse()` / `api.posts.read({id})` / `api.posts.edit({id, ...})`
   - Server-side only (keys must remain secret)

5. **Code Injection** — Ghost Admin allows injecting HTML/JS into `<head>` and footer
   - Per-site or per-post `codeinjection_head` / `codeinjection_foot` fields

6. **Themes** — Handlebars templates, full control over front-end rendering

### Feasibility Assessment

**Can we replicate the WordPress plugin's functionality? YES — but the architecture is fundamentally different.**

#### WordPress Plugin Model (current)
- Runs *inside* WordPress as a PHP plugin
- Hooks into `publish_post` / `post_updated` actions directly
- Exposes WP REST endpoints (`/wp-json/encypher-provenance/v1/sign`)
- Has Gutenberg sidebar panel for manual signing
- Stores metadata in post meta fields
- Renders verification badge on front-end via theme hooks

#### Ghost Integration Model (proposed)
- Runs as an **external Node.js microservice** (not inside Ghost)
- Listens for Ghost webhooks (`post.published`, `post.published.edited`)
- Uses Ghost Admin API to read post content, sign via Encypher API, then write back signed content
- No native editor sidebar — would need a companion web UI or rely on automatic signing
- Can store provenance metadata via Ghost's `codeinjection_head` field or custom tags
- Front-end verification badge injected via theme helper or code injection

### Recommended Architecture

```
┌─────────────┐     webhook POST      ┌──────────────────────┐
│  Ghost CMS   │ ──────────────────►  │  Encypher Ghost      │
│  (publisher) │                       │  Integration Service │
└──────┬───────┘                       │  (Node.js)           │
       │                               └──────┬───┬───────────┘
       │  Admin API (read/write posts)         │   │
       ◄───────────────────────────────────────┘   │
                                                   │ POST /api/v1/sign
                                                   │ POST /api/v1/verify
                                               ┌───▼───────────────┐
                                               │  Encypher          │
                                               │  Enterprise API    │
                                               └───────────────────┘
```

**Flow:**
1. Author publishes/updates a post in Ghost Admin
2. Ghost fires `post.published` or `post.published.edited` webhook to our service
3. Service receives webhook, extracts post ID from payload
4. Service calls Ghost Admin API to `GET /ghost/api/admin/posts/{id}/?formats=html`
5. Service extracts plain text from HTML content
6. Service calls Encypher Enterprise API `POST /api/v1/sign` with the text
7. Service receives signed content with invisible C2PA embeddings
8. Service calls Ghost Admin API `PUT /ghost/api/admin/posts/{id}/` to update the post HTML with signed content
9. Optionally injects verification badge script via `codeinjection_foot`

### Key Technical Considerations

1. **Infinite Loop Prevention**: When we update the post via Admin API after signing, Ghost will fire another `post.published.edited` webhook. Must track which posts are already being processed (e.g., in-memory set or Redis) and skip re-processing.

2. **Content Format**: Ghost uses Lexical JSON internally but exposes HTML. We should:
   - Read content as HTML (`?formats=html`)
   - Sign the text extracted from HTML
   - Write back using `{source: 'html'}` to let Ghost convert back to Lexical

3. **updated_at Requirement**: Ghost's PUT endpoint requires the current `updated_at` timestamp to prevent conflicts. Must always read the post first, then use that timestamp in the update.

4. **No Editor Integration**: Unlike WordPress's Gutenberg sidebar, Ghost has no plugin UI extension point. Options:
   - **Automatic only** (webhook-driven, zero UI in Ghost editor)
   - **Companion dashboard** (separate web app for config/status)
   - **Ghost Admin code injection** (inject a small JS widget)

5. **Metadata Storage**: Ghost posts don't have arbitrary meta fields. Options:
   - Use internal tags (e.g., `#encypher-signed`)
   - Store in `codeinjection_head` as a JSON `<script>` block
   - Maintain a separate database in the integration service

6. **Self-hosted vs Ghost(Pro)**: Webhooks and Admin API work on both. The integration service just needs network access to the Ghost instance.

## Implementation Summary

Full integration built at `integrations/ghost-provenance/`.

### Files Created
- `package.json`, `tsconfig.json`, `.env.example` — Project scaffolding
- `src/config.ts` — Environment-based configuration
- `src/html-utils.ts` — HTML text extraction/embedding with Ghost card handling (mirrors WP HtmlParser)
- `src/ghost-client.ts` — Ghost Admin API wrapper using `@tryghost/admin-api`
- `src/encypher-client.ts` — Enterprise API client (sign/verify)
- `src/metadata-store.ts` — SQLite store for signing records
- `src/webhook-handler.ts` — Express routes for Ghost webhooks with loop prevention
- `src/signer.ts` — Orchestration: read → sign → embed → write-back → record
- `src/badge-injector.ts` — Verification badge code injection
- `src/index.ts` — Express app entry point
- `src/types/tryghost-admin-api.d.ts` — Type declarations for Ghost Admin API
- `tests/html-utils.test.ts` — 45 unit tests for HTML parsing/Ghost cards
- `tests/webhook-handler.test.ts` — 11 unit tests for webhook handling/loop prevention
- `docker-compose.yml` — Ghost + MySQL + Enterprise API + PostgreSQL + Integration Service
- `Dockerfile` — Production container
- `vitest.config.ts` — Test configuration
- `theme-helpers/partials/encypher-badge.hbs` — Handlebars partial for Ghost themes
- `README.md` — Full setup and usage documentation

### Test Results
- **56 tests passing** (45 html-utils + 11 webhook-handler)
- TypeScript build clean (0 errors)

### Ghost Card/Tag Handling
- Skips: `kg-image-card`, `kg-gallery-card`, `kg-video-card`, `kg-audio-card`, `kg-embed-card`, `kg-code-card`, `kg-html-card`
- Extracts text from: `kg-callout-card`, `kg-toggle-card`, `kg-bookmark-card`
- Preserves all user tags during signing, adds `#encypher-signed` internal tag
- Tags passed as metadata to Enterprise API for attribution

### E2E Test Results (2026-02-13)

Full signing flow verified with Docker Compose stack:
1. Ghost webhook `post.published` → integration service
2. Read post via Ghost Admin API (234 chars extracted from 302 bytes HTML)
3. Enterprise API `/sign` called → 3 segments signed
4. Signed text embedded back (2022 VS chars, 4331 bytes HTML)
5. Ghost post updated with signed HTML + `#encypher-signed` tag + verification badge (1302 chars in `codeinjection_foot`)

### Docker Networking
- Ghost-provenance container joins `encypher-network` (external) to reach `encypher-enterprise-api:8000` directly
- Avoids `host.docker.internal` Host header issues with Traefik/Enterprise API
- Ghost + MySQL on default compose network; ghost-provenance bridges both

### Fixes Applied During E2E
- **Lazy GhostClient init**: `@tryghost/admin-api` validates key format eagerly; deferred to `getApi()` so service starts without key
- **Graceful startup**: Service warns but doesn't crash-loop when `GHOST_ADMIN_API_KEY` is missing
- **Docker networking**: Joined `encypher-network` to reach Enterprise API by container name

## Suggested Git Commit Message

```
feat(integrations): add Ghost CMS provenance integration

New external Node.js microservice that brings Encypher C2PA signing
to Ghost CMS via webhooks + Admin API. Mirrors the WordPress plugin's
functionality with Ghost-specific adaptations.

- Webhook-driven auto-signing on post.published / post.published.edited
- Ghost Koenig card handling (callouts, toggles, bookmarks extracted;
  images, embeds, code blocks skipped)
- Loop prevention for webhook → Admin API update cycles
- SQLite metadata store for signing records and provenance chain
- Verification badge via code injection or Handlebars theme partial
- Tag preservation + #encypher-signed internal tag
- Lazy GhostClient init (graceful startup without API key)
- Docker Compose for local dev (Ghost + MySQL + integration service)
- Joins encypher-network to reach Enterprise API container directly
- 56 unit tests passing, TypeScript build clean
- E2E verified: 2022 VS chars embedded, badge injected, tag added

Ref: PRDs/CURRENT/PRD_Ghost_Provenance_Integration.md
```
