# Encypher Provenance Ghost Integration

This integration brings Encypher's C2PA signing and verification workflow to **Ghost CMS**. It runs as an external Node.js microservice that listens for Ghost webhooks and automatically signs published content with C2PA-compliant invisible embeddings via the Enterprise API.

## Architecture

Unlike the WordPress plugin (which runs inside WordPress as a PHP plugin), Ghost has no native plugin system. This integration runs as a **standalone service** that communicates with Ghost via its Admin API and webhooks.

```
Ghost CMS ──webhook──► Encypher Ghost Service ──sign──► Traefik (port 8000) ──► Enterprise API
    ▲                         │
    └──Admin API (update)─────┘
```

### Flow

1. Author publishes/updates a post in Ghost Admin
2. Ghost fires `post.published` or `post.published.edited` webhook
3. Service reads post content via Ghost Admin API
4. Service extracts plain text from HTML (handling Ghost cards, tags, etc.)
5. Service calls Encypher Enterprise API `POST /api/v1/sign`
6. Service embeds signed text back into HTML
7. Service updates post in Ghost via Admin API
8. Service adds `#encypher-signed` internal tag and verification badge

## Features

- **Auto-sign on publish** — Webhook-driven, zero manual intervention
- **Auto-sign on update** — Re-signs with `c2pa.edited` action and provenance chain
- **Ghost card handling** — Correctly extracts text from callouts, toggles, bookmarks; skips images, embeds, code blocks
- **Tag preservation** — All existing Ghost tags are preserved during signing
- **Loop prevention** — In-flight tracking prevents infinite webhook loops
- **Content hash caching** — Skips re-signing when content hasn't changed
- **Verification badge** — Injected via `codeinjection_foot` or theme partial
- **Provenance chain** — Edit history tracked with ingredient references
- **SQLite metadata store** — Local database for signing records

## Quick Start

### Prerequisites

- Node.js 20+
- A Ghost instance (self-hosted or Ghost(Pro))
- An Encypher API key ([sign up](https://dashboard.encypherai.com/signup))

### 1. Install

```bash
cd integrations/ghost-provenance
npm install
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your Ghost and Encypher credentials
```

### 3. Create a Ghost Custom Integration

1. In Ghost Admin, go to **Settings → Integrations → Add custom integration**
2. Name it "Encypher Provenance"
3. Copy the **Admin API Key** and paste it into `.env` as `GHOST_ADMIN_API_KEY`
4. Add webhooks:
   - **post.published** → `http://localhost:3000/api/ghost/post-published`
   - **post.published.edited** → `http://localhost:3000/api/ghost/post-updated`
   - **page.published** → `http://localhost:3000/api/ghost/page-published`
   - **page.published.edited** → `http://localhost:3000/api/ghost/page-updated`

### 4. Start

```bash
npm run dev    # Development with hot reload
npm run build && npm start  # Production
```

## Docker Compose (Local Development)

The `docker-compose.yml` runs Ghost + MySQL + the integration service. It expects the **main dev stack** (Enterprise API, Traefik, etc.) to already be running on the host via `start-dev.sh`. The integration service routes API requests through Traefik on host port 8000 using `host.docker.internal`.

### Prerequisites

```bash
# Start the main dev stack first (from repo root)
./start-dev.sh
```

### Start Ghost + Integration Service

```bash
cd integrations/ghost-provenance

# Set your Ghost Admin API key (obtained after Ghost setup)
export GHOST_ADMIN_API_KEY=your_key_here

# Start Ghost + integration service
docker compose up --build

# Ghost will be at http://localhost:2368
# Integration service at http://localhost:3100
# Enterprise API already at http://localhost:8000 (via Traefik)
```

After Ghost starts:
1. Complete the Ghost setup wizard at `http://localhost:2368/ghost`
2. Go to **Settings → Integrations → Add custom integration**
3. Copy the **Admin API Key**
4. Set it as `GHOST_ADMIN_API_KEY` and restart: `GHOST_ADMIN_API_KEY=<key> docker compose up -d`
5. Configure webhooks (use `http://ghost-provenance:3000` as the host since services are on the same Docker network)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info and available endpoints |
| `/api/health` | GET | Health check |
| `/api/ghost/post-published` | POST | Webhook: post published |
| `/api/ghost/post-updated` | POST | Webhook: post updated |
| `/api/ghost/page-published` | POST | Webhook: page published |
| `/api/ghost/page-updated` | POST | Webhook: page updated |
| `/api/ghost/webhook` | POST | Generic webhook (auto-detects type) |
| `/api/sign` | POST | Manual sign: `{ postId, postType }` |
| `/api/status/:postId` | GET | Get signing status for a post |

## Ghost Card Handling

The integration correctly handles Ghost's Koenig editor cards:

| Card Type | Behavior |
|-----------|----------|
| Paragraphs, headings, lists, tables, blockquotes | Text extracted and signed |
| `kg-callout-card` | Callout text extracted and signed |
| `kg-toggle-card` | Heading + content text extracted and signed |
| `kg-bookmark-card` | Title + description text extracted and signed |
| `kg-image-card`, `kg-gallery-card` | Skipped (no text) |
| `kg-video-card`, `kg-audio-card` | Skipped (no text) |
| `kg-embed-card` | Skipped (no text) |
| `kg-code-card`, `kg-html-card` | Skipped (code/raw HTML) |

## Theme Integration

### Option 1: Code Injection (automatic)

When `BADGE_ENABLED=true`, the service automatically injects a verification badge script into each signed post's `codeinjection_foot`. No theme changes needed.

### Option 2: Handlebars Partial (custom themes)

Copy `theme-helpers/partials/encypher-badge.hbs` into your Ghost theme's `partials/` directory, then include it in `post.hbs`:

```handlebars
{{> encypher-badge}}
```

The partial checks for the `#encypher-signed` internal tag and renders a badge if present.

## Testing

```bash
npm test          # Run all tests
npm run test:watch  # Watch mode
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GHOST_URL` | `http://localhost:2368` | Ghost instance URL |
| `GHOST_ADMIN_API_KEY` | (required) | Ghost Admin API key |
| `GHOST_API_VERSION` | `v5.0` | Ghost API version |
| `ENCYPHER_API_BASE_URL` | `http://localhost:8000/api/v1` | Enterprise API URL |
| `ENCYPHER_API_KEY` | (required) | Encypher API key |
| `PORT` | `3000` | Service port |
| `LOG_LEVEL` | `info` | Log level (debug, info, warn, error) |
| `AUTO_SIGN_ON_PUBLISH` | `true` | Auto-sign when posts are published |
| `AUTO_SIGN_ON_UPDATE` | `true` | Auto-sign when published posts are updated |
| `SIGNING_TIER` | `free` | Encypher tier (free, pro, enterprise) |
| `MANIFEST_MODE` | `micro_ecc_c2pa` | C2PA manifest mode |
| `SEGMENTATION_LEVEL` | `sentence` | Signing granularity |
| `DB_PATH` | `./data/ghost-provenance.db` | SQLite database path |
| `BADGE_ENABLED` | `true` | Inject verification badge |
| `VERIFY_BASE_URL` | `https://verify.encypherai.com` | Verification URL base |
| `WEBHOOK_SECRET` | (optional) | Secret for verifying webhook signatures |
