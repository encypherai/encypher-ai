# Encypher CDN Provenance — Fastly Compute@Edge

Intercepts image responses from your origin and injects a `C2PA-Manifest-URL` response header
by looking up the canonical image URL against the Encypher API. This enables downstream clients
and browsers to discover and verify C2PA provenance metadata without modifying the origin.

## Required Fastly service configuration

**Backends** (add in the Fastly console):
- `origin` — your existing publisher origin server
- `encypher_api` — `api.encypher.com` (port 443, TLS)

**Edge Dictionary** — create a dictionary named `encypher_config` with keys:
- `api_base_url` — e.g. `https://api.encypher.com`
- `cache_ttl_s` — e.g. `3600`

## Prerequisites

- [Fastly CLI](https://developer.fastly.com/reference/cli/) (`fastly` command)
- Rust toolchain with the `wasm32-wasi` target: `rustup target add wasm32-wasi`

## Deploy

```bash
fastly compute publish
```
