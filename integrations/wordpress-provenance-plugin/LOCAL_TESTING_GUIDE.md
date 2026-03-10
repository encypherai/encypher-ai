# WordPress Provenance Plugin - Local Testing Guide

## Overview

This guide covers two paths:

1. **Automated bootstrap** (recommended for demo prep) -- one command spins up a fresh
   WordPress instance, provisions an Encypher account, imports 10 curated articles,
   signs them all, and validates the result.

2. **Manual setup** -- step-by-step instructions for exploring or developing the plugin.

---

## Prerequisites

- Docker and Docker Compose installed and running
- The main Encypher dev stack running (Enterprise API on `localhost:8000`):
  ```bash
  # From the repo root
  docker compose up -d
  ```
- Python 3.11+ available as `python3`
- Port 8888 free (the WordPress sandbox runs there)

Verify the Enterprise API is healthy before proceeding:
```bash
curl -fsS http://localhost:8000/health && echo "OK"
```

---

## Path 1: Automated bootstrap (demo prep)

```bash
cd integrations/wordpress-provenance-plugin
./bootstrap_clone_env.sh
```

The script will:
- Tear down any previous sandbox instance
- Start a fresh WordPress stack on `http://localhost:8888`
- Install WordPress and activate the Encypher plugin
- Create a fresh demo Encypher account and verify it
- Generate an API key and configure the plugin automatically
- Import 10 curated editorial posts
- Sign all 10 posts
- Write a summary to `.wordpress-clone-summary.json`

When complete, open `http://localhost:8888` in a browser.

### Overridable environment variables

| Variable | Default | Purpose |
|---|---|---|
| `WP_URL` | `http://localhost:8888` | Public WordPress URL |
| `API_GATEWAY_BASE` | `http://localhost:8000/api/v1` | Enterprise API (host side) |
| `WP_API_BASE` | `http://host.docker.internal:8000/api/v1` | Enterprise API (container side) |
| `ENCYPHER_POSTGRES_CONTAINER` | `encypher-postgres` | Auth DB container name |
| `DISPLAY_NAME` | `Encypher Review Sandbox` | Demo org display name |
| `PROJECT_NAME` | `wordpress-provenance-clone` | Docker Compose project name |

Example with overrides:
```bash
ENCYPHER_POSTGRES_CONTAINER=my-postgres PROJECT_NAME=demo2 ./bootstrap_clone_env.sh
```

### Expected output

```
Preflight: checking Enterprise API is reachable...
  -> Enterprise API OK at http://localhost:8000/health
Preflight: checking Postgres container 'encypher-postgres' is accessible...
  -> Postgres container OK
Generating curated 10-post dataset...
Resetting isolated WordPress clone stack...
Installing WordPress...
Provisioning fresh Encypher demo workspace...
Configuring plugin...
Running connection test...
Importing sample articles...
Signing remaining imported posts...
Clone environment ready. Summary written to .wordpress-clone-summary.json
```

---

## Path 2: Manual setup

### Step 1: Start the Enterprise API

From the repo root:
```bash
docker compose up -d
```

Or run the API directly (from `enterprise_api/`):
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify:
```bash
curl http://localhost:8000/health
```

### Step 2: Start WordPress

```bash
cd integrations/wordpress-provenance-plugin
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml up -d
```

Check status:
```bash
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml ps
```

Wait for WordPress to be ready:
```bash
until curl -fsS http://localhost:8888 >/dev/null 2>&1; do echo "waiting..."; sleep 3; done
echo "WordPress ready"
```

### Step 3: Install WordPress and activate plugin

```bash
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml \
  run --rm wp-cli core install \
  --url=http://localhost:8888 \
  --title="Encypher Demo" \
  --admin_user=admin \
  --admin_password=TestPassword123! \
  --admin_email=admin@example.com \
  --skip-email

docker compose -p wordpress-provenance-clone -f docker-compose.test.yml \
  run --rm wp-cli plugin activate encypher-provenance

docker compose -p wordpress-provenance-clone -f docker-compose.test.yml \
  run --rm wp-cli rewrite structure '/%postname%/' --hard
```

### Step 4: Configure plugin via admin UI

Go to `http://localhost:8888/wp-admin` (admin / TestPassword123!).

Navigate to **Encypher -> Settings** and set:
- **API Base URL:** `http://host.docker.internal:8000/api/v1`
- **API Key:** (your key from the Encypher dashboard or bootstrap summary)
- **Auto-sign on publish:** enabled
- **Auto-sign on update:** enabled
- **Metadata format:** C2PA

### Step 5: Generate and import demo content

Generate the 10-post seed dataset:
```bash
python3 generate_marketing_blog_seed.py --curated --limit 10 \
  --output plugin/encypher-provenance/data/marketing-blog-posts.json
```

Import into WordPress:
```bash
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml \
  exec -T wordpress \
  php /var/www/html/wp-content/plugins/encypher-provenance/import_marketing_blog_posts.php
```

### Step 6: Verify signing

Check signed post count:
```bash
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml \
  run --rm wp-cli eval '
$q = new WP_Query([
    "post_type" => "post",
    "post_status" => "publish",
    "posts_per_page" => -1,
    "fields" => "ids",
    "meta_query" => [["key" => "_encypher_marked", "value" => "1"]],
]);
echo count($q->posts) . " posts signed\n";
'
```

---

## End-to-end verification checklist

After bootstrap or manual setup, verify the following before a demo:

- [ ] `http://localhost:8888` loads the WordPress site
- [ ] `http://localhost:8888/wp-admin` is accessible (admin / TestPassword123!)
- [ ] **Encypher -> Content** shows 10 signed posts
- [ ] Opening a post on the frontend shows the verification badge (bottom-right)
- [ ] Clicking the badge opens the verification modal with provenance data
- [ ] **Encypher -> Settings** shows "Connected" status
- [ ] Dashboard integrations page shows the WordPress install

---

## Debugging

### View WordPress debug log

```bash
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml \
  exec wordpress tail -f /var/www/html/wp-content/debug.log
```

### View Enterprise API logs

```bash
docker logs encypher-enterprise-api -f
```

### Test sign endpoint manually

Get a WP nonce from the browser (DevTools -> Network, look for `X-WP-Nonce` in any WP REST call), then:

```bash
curl -s -X POST http://localhost:8888/wp-json/encypher-provenance/v1/sign \
  -H "X-WP-Nonce: <nonce>" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 1}' | python3 -m json.tool
```

### Common issues

**Preflight fails: "Enterprise API is not reachable"**
- Run `docker compose up -d` from the repo root
- Wait 10-15 seconds and retry

**Preflight fails: "Cannot reach Postgres container"**
- List containers: `docker ps --format "{{.Names}}" | grep postgres`
- Pass the correct name: `ENCYPHER_POSTGRES_CONTAINER=<name> ./bootstrap_clone_env.sh`

**Badge not appearing on frontend**
- Check "Show C2PA badge" is enabled in Settings
- Verify the post is signed (meta `_encypher_marked = 1`)
- Clear browser cache

**Verification modal shows error**
- Check Enterprise API is running: `curl http://localhost:8000/health`
- Check WordPress debug log for the specific error

---

## Tear down

```bash
docker compose -p wordpress-provenance-clone -f docker-compose.test.yml down -v
```

This removes all containers and volumes for the sandbox. The main Encypher stack is unaffected.
