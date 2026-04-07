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

## Troubleshooting

**Worker is deployed but articles are not signed.**

Check the `X-Encypher-Provenance` response header. A value of `active` means the
page was signed. Other values indicate why it was skipped:

| Header Value | Meaning | Fix |
|---|---|---|
| `active` | Page was signed successfully | None needed |
| `skipped:empty` | Extracted text was below 50 characters | Page has no article content, or detection missed it |
| `skipped:oversized` | Extracted text exceeded 50 KB | Increase `MAX_TEXT_LENGTH` or accept partial signing |
| `skipped:error` | API or embedding error (fail-open) | Check Cloudflare Workers logs for details |
| Header absent | Request was not intercepted by the worker | Verify your Cloudflare route pattern matches the URL |

**Detection picks up the wrong content (nav, sidebar, footer text).**

Set the `ARTICLE_SELECTOR` environment variable to a CSS selector that targets
your article body. Example:

```toml
[vars]
ARTICLE_SELECTOR = ".my-post-body"
```

Supported selector forms: tag name (`article`), class (`.post-content`),
attribute (`[data-testid="article-body"]`). The selector must match a single
container element. Restart the worker after changing the variable.

**Markers appear as visible characters.**

The provenance markers use Unicode variation selectors, which are invisible in
all modern browsers and text editors. If you see unexpected characters, confirm
you are not viewing the raw HTML source in a hex editor. Markers are invisible
in rendered HTML, plain text copy-paste, and standard text editors.

**KV namespace errors on deploy.**

If deploying manually (not via the Deploy button), replace the placeholder
namespace ID in `wrangler.toml` with your actual KV namespace ID. Run
`wrangler kv:namespace create PROVENANCE_CACHE` to create one.

---

## API Reference

The worker communicates with four backend endpoints. Publishers do not call
these directly. They are documented here for transparency and debugging.

### POST /api/v1/public/cdn/provision

Auto-provisions a domain on first request. Public, no authentication required.

```json
// Request
{
  "domain": "example.com",
  "worker_version": "1.0.0"
}

// Response
{
  "org_id": "org_cdn_a1b2c3d4e5f6",
  "domain_token": "dtk_...",
  "dashboard_url": "https://dashboard.encypher.com/cdn/example.com",
  "claim_url": "https://dashboard.encypher.com/claim/org_cdn_a1b2c3d4e5f6"
}
```

### POST /api/v1/public/cdn/sign

Signs article text and returns an embedding plan. Public, rate-limited by org
quota (1,000 unique signs/month on the free tier).

```json
// Request
{
  "text": "extracted article text...",
  "page_url": "https://example.com/article/slug",
  "org_id": "org_cdn_a1b2c3d4e5f6",
  "options": {
    "return_embedding_plan": true
  }
}

// Response
{
  "embedding_plan": {
    "index_unit": "codepoint",
    "operations": [
      {"insert_after_index": 42, "marker": "\ufe00\ufe01"}
    ]
  },
  "document_id": "doc_...",
  "verification_url": "https://encypher.com/verify/doc_...",
  "content_hash": "sha256:abcdef...",
  "cached": false,
  "signer_tier": "encypher_free"
}
```

Duplicate requests (same domain + content hash) return the cached plan with no
quota charge.

### GET /api/v1/public/cdn/manifest/{record_id}

Returns manifest metadata for a signed content record. Public, CORS-enabled.

### POST /api/v1/public/cdn/claim

Claims a CDN domain for dashboard access. Requires authentication.

```json
// Request
{
  "domain": "example.com"
}

// Response
{
  "status": "verification_initiated",
  "domain": "example.com"
}
```

The backend verifies domain ownership by fetching
`https://example.com/.well-known/encypher-verify` and confirming the
domain token matches.

---

## FAQ

**What text is signed?**

The worker signs visible article text only. Navigation, footers, sidebars, ads,
scripts, and metadata are excluded. The detection chain identifies the article
boundary using semantic HTML, CMS class names, and Schema.org microdata.

**What data is stored?**

The Encypher API stores a content hash, the page URL, a document ID, and the
signing timestamp. The full article text is not stored. The embedding plan
(marker positions and sequences) is cached in Cloudflare KV for one hour and in
the Encypher backend for deduplication.

**Who owns the signed content?**

The publisher owns the content. Signing does not transfer any intellectual
property rights. The provenance record attributes the content to the publisher's
domain at the time of signing.

**Do markers affect SEO?**

No. Unicode variation selectors are zero-width, invisible characters that do not
affect rendering, indexing, or search ranking. Google's crawler processes the
same visible text as any reader.

**Do markers survive copy-paste?**

Yes. Variation-selector markers survive copy-paste in Chrome, Firefox, Safari,
and Edge. They survive email forwarding, RSS aggregation, and scraping. This is
the core design property that makes provenance tracking work after content
leaves the original site.

**What happens if the Encypher API is down?**

The worker serves the original unmodified HTML. All errors are fail-open.
Readers never see an error page or broken content. When the API recovers,
signing resumes automatically on the next cache miss.

**Can I use this with a custom CMS or static site generator?**

Yes. If the auto-detection chain does not find your article content, set the
`ARTICLE_SELECTOR` environment variable to a CSS selector targeting your article
body container. Any site that serves HTML over Cloudflare is compatible.

**Is the worker open source?**

The worker source code is provided for transparency and auditability. The
signing API, marker embedding protocol, and verification infrastructure are
proprietary. See the LICENSE file for terms.

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
