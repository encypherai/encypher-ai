# Encypher Edge Provenance Worker

Embeds invisible, copy-paste-survivable content provenance markers into HTML
articles at the CDN edge. Publishers deploy once and every article is signed
at sentence-level granularity, with no changes to their CMS, build pipeline,
or publishing workflow.

[![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/encypher/cloudflare-worker-provenance)

---

## How It Works

**1. Deploy.** Click the button above. Cloudflare clones this worker into your
account and prompts you to set a route, typically `*yourdomain.com/*`. No
configuration is required to start signing.

**2. Auto-provision.** On the first article request, the worker registers your
domain with the Encypher API and caches the result in KV storage. Subsequent
requests skip this step entirely.

**3. Sign.** Every article response is intercepted before it reaches the
reader. The worker extracts visible text, calls the Encypher signing API, and
splices Unicode variation-selector markers into the HTML at the positions the
API specifies. The signed HTML is served in place of the original.

The markers are invisible to readers and survive copy-paste, scraping, and
aggregation. When content is lifted and republished elsewhere, the provenance
travels with it.

---

## What Gets Signed

The worker finds article content using a detection chain ordered by
prevalence. It evaluates each method in sequence and uses the first match.

| Priority | Method | Description |
|---|---|---|
| P0 | Publisher override | `ARTICLE_SELECTOR` config var |
| P1 | `<article>` tag | Covers ~50% of content sites; picks the paragraph-richest when multiple exist |
| P2 | CMS class names | `entry-content`, `gh-content`, `w-richtext`, `sqs-block-content`, and others |
| P3 | Schema.org microdata | `[itemprop="articleBody"]` |
| P4 | `<main>` / `role="main"` | Semantic HTML landmark |
| P5 | JSON-LD `articleBody` | Structured data, used for validation cross-check |
| P6 | Largest paragraph cluster | Heuristic: container with the highest `<p>` density, minimum 5 paragraphs |
| P7 | `<body>` fallback | Last resort |

Once the boundary is found, the worker extracts only the visible text,
discarding tags and scripts. The Encypher API returns an embedding plan
specifying byte offsets and marker sequences. The worker splices markers at
those offsets and serves the modified HTML.

All errors are fail-open. If the API is unreachable, the boundary cannot be
found, or the signing quota is exhausted, the original unmodified HTML is
served. Readers never see an error.

---

## Configuration

All configuration is optional. The worker signs articles with zero config.
Add any of the following to the `[vars]` block in `wrangler.toml`, or set
secrets with `wrangler secret put`.

```toml
[vars]
# Override article detection with a CSS selector.
# Supports tag names, .class, and [attr=value] forms.
# Default: auto-detect via the 8-priority chain.
ARTICLE_SELECTOR = ".my-article-class"

# Minimum visible text length (characters) required to sign.
# Pages shorter than this are passed through unsigned.
# Default: 50
MIN_TEXT_LENGTH = "50"

# Maximum visible text length (characters) to sign.
# Text beyond this limit is truncated before signing.
# Default: 51200 (50 KB)
MAX_TEXT_LENGTH = "51200"

# Enterprise API key. When set, authenticated endpoints are used and
# your org's enterprise-tier settings apply automatically.
# Set as a secret rather than plaintext:
#   wrangler secret put ENCYPHER_API_KEY
```

The `PROVENANCE_CACHE` KV namespace is required and is provisioned
automatically during deploy. Replace the placeholder ID in `wrangler.toml`
with your actual namespace ID if deploying manually:

```toml
[[kv_namespaces]]
binding = "PROVENANCE_CACHE"
id = "YOUR_KV_NAMESPACE_ID"
```

---

## Supported CMS Platforms

| Platform | Detection Method |
|---|---|
| WordPress (Classic and Block themes) | `entry-content`, `wp-block-post-content`, `<article>` |
| Ghost (Casper theme) | `gh-content` |
| Squarespace | `sqs-block-content` |
| Webflow | `w-richtext` |
| Substack | `body markup` |
| Medium | `<article>` |
| Hugo | `<article>` or `<main>` |
| Jekyll (Minima theme) | `post-content` |
| News publishers (AP, wire feeds) | `RichTextStoryBody`, `article-body`, `story-body` |
| Microformats2 / IndieWeb | `e-content` |
| Custom HTML | `ARTICLE_SELECTOR` override, or automatic heuristic |

---

## Verification

Copy any text from a signed article and paste it at
[encypher.com/verify](https://encypher.com/verify). The provenance survives
the copy-paste. The verifier extracts the embedded markers, resolves the
signing record, and returns the source domain, signing timestamp, and
document ID.

You can also check whether a page has been processed by inspecting the
response header:

```
X-Encypher-Provenance: active
```

Other values are `skipped:oversized`, `skipped:empty`, and `skipped:error`.

The worker also exposes a machine-readable endpoint at
`/.well-known/encypher-verify` that returns the domain token and org ID for
the domain:

```json
{
  "domain_token": "...",
  "org_id": "...",
  "worker_version": "1.0.0"
}
```

---

## Enterprise Features

The free tier provides full sentence-level signing with micro+ECC+C2PA
markers for every article. Enterprise adds:

- **Fingerprinting.** Per-reader marker variation for print leak detection and
  downstream copy tracking.
- **Dual binding.** Each document is bound to both the page URL and the
  signing certificate, making content relocation detectable.
- **Per-segment rights.** Granular licensing metadata embedded at the sentence
  level, specifying permitted reuse, syndication, and attribution terms.

Upgrade via the [Encypher dashboard](https://dashboard.encypher.com). No
worker reconfiguration is required. Set your `ENCYPHER_API_KEY` secret once
and enterprise features activate automatically at the API level.

---

## Technical Overview

The worker intercepts every `GET` request for `text/html` responses with a
200 status code. Static assets, admin paths, feeds, and sitemaps are skipped
before the origin is fetched.

Processing pipeline per request:

1. Fetch the origin HTML response.
2. Locate the article boundary using the detection chain described above.
3. Extract text fragments with their byte offsets relative to the boundary.
4. Assemble visible text and compute a SHA-256 content hash for the cache key.
5. Check KV for a cached embedding plan. On a hit, skip to step 8.
6. On a miss, ensure the domain is provisioned (cached in KV after first
   registration). Sign the content via the Encypher API.
7. Cache the resulting embedding plan in KV for subsequent identical page
   loads.
8. Apply the embedding plan: splice Unicode variation-selector marker
   sequences into the HTML at the byte offsets specified by the API.
9. Inject a verification comment before `</body>` and serve the modified HTML.

The embedding plan is keyed on a content hash, so the API is called at most
once per unique article version. Cached plans are applied locally on
subsequent requests with no additional API round-trip.

---

## Development

Run the test suite:

```bash
npm test
```

Tests cover the three core modules: boundary detection, fragment extraction,
and embedding plan application. Test files are in `tests/`.

Start a local dev server with live reload:

```bash
npm run dev
```

`wrangler dev` proxies requests to `localhost:8787` and connects to your
Cloudflare account for KV access. Set your `ENCYPHER_API_KEY` in a `.dev.vars`
file (never commit this file):

```
ENCYPHER_API_KEY=your_key_here
```

Deploy to production:

```bash
npm run deploy
```

---

## License

Copyright (c) 2026 Encypher Corporation. All rights reserved.

This software is proprietary. The worker source code is provided for
transparency and auditability. The signing API, marker embedding protocol, and
verification infrastructure are not open source. Redistribution or use outside
of the Encypher platform requires a written license agreement.
