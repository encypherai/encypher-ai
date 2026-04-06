# Changelog

## 1.0.0 (2026-04-06)

Initial release of the Encypher Edge Provenance Worker.

### Features

- Sentence-level provenance markers (micro+ECC+C2PA) embedded at the CDN edge
- Copy-paste-survivable Unicode variation-selector markers
- 8-priority article boundary detection chain covering WordPress, Ghost,
  Squarespace, Webflow, Substack, Hugo, Jekyll, and custom HTML
- Auto-provisioning: worker registers domain with Encypher API on first request
- KV caching: embedding plans cached per content hash (1h TTL)
- Fail-open: all errors serve unmodified HTML
- Zero-config deployment via Cloudflare Deploy button
- Optional ARTICLE_SELECTOR override for custom layouts
- Optional ENCYPHER_API_KEY for enterprise features
- Verification endpoint at /.well-known/encypher-verify
