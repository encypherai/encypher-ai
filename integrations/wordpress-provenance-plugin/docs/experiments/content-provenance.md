# Content Provenance Experiment

**Status:** Draft for upstream contribution to WordPress/ai
**Experiment slug:** `content-provenance`
**Requires:** Encypher API key (free tier: 1,000 signs/month)

## Overview

The Content Provenance experiment automatically embeds C2PA-compatible cryptographic provenance into AI-generated content as it flows through WordPress/ai experiments. When any AI experiment (Title Generation, Excerpt Generation, Summarization, Review Notes, Alt Text) produces output, this experiment signs the content via the Encypher API before it is committed to the post.

The result is content that:
- Carries a cryptographic record of which AI model generated it, when, and from what source
- Embeds an invisible Unicode watermark (variation selector technique) that survives copy-paste out of WordPress
- Can be publicly verified via `curl POST https://api.encypherai.com/api/v1/verify`
- Provides audit trail for editorial compliance (EU AI Act, etc.)

## Architecture

```
WordPress/ai Experiment  →  content output filter  →  Encypher Sign API
                                                              ↓
                                                     Signed text (C2PA manifest embedded)
                                                              ↓
                                                     Returned to experiment output
```

The `Content_Provenance` class hooks into all WordPress/ai experiment output filters:
- `wp_ai_experiment_title_generation_result`
- `wp_ai_experiment_excerpt_generation_result`
- `wp_ai_experiment_summary_generation_result`
- `wp_ai_experiment_review_notes_result`
- `wp_ai_experiment_alt_text_result`

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `api_key` | (required) | Encypher API key. Free tier: 1,000 signs/month |
| `embed_watermark` | `true` | Embed invisible Unicode watermark |
| `sign_alt_text` | `false` | Also sign image alt text (shorter strings) |

## How to Test

1. Activate both WordPress/ai and Encypher Provenance plugins
2. Enable the Content Provenance experiment in WordPress/ai settings
3. Open any post in the Gutenberg editor
4. Use a WordPress/ai experiment (e.g., Title Generation)
5. Observe the generated title — it now carries a C2PA manifest
6. Verify:
   ```bash
   curl -X POST https://api.encypherai.com/api/v1/verify \
     -H "Content-Type: application/json" \
     -d '{"text": "<paste signed title here>"}'
   ```
7. The response will include the signing model, timestamp, and content hash

## API

### Verify a signed text

```bash
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "Your AI-generated content here (with embedded Unicode watermark)"}'
```

Response:
```json
{
  "verified": true,
  "metadata": {
    "generator": "gpt-4o",
    "provider": "openai",
    "signed_at": "2026-03-10T12:00:00Z",
    "experiment": "title_generation",
    "post_id": 42
  }
}
```

## Upstream PR Checklist

- [ ] `Content_Provenance` class extends `Abstract_Experiment`
- [ ] Settings registered via `get_fields()` returning `[api_key, embed_watermark]`
- [ ] Experiment enabled/disabled via `is_enabled()` → checks option
- [ ] Hooks registered only when enabled
- [ ] Unit tests: mock Encypher API, assert signed output is returned
- [ ] E2E test: WP env, activate both plugins, Title Generation → verify signed output
- [ ] Changelog entry
- [ ] Screenshots for PR (before/after, settings UI)

## Relation to Encypher Coalition

When enrolled in the Encypher Coalition (via Encypher plugin settings), every piece of signed AI content is tracked in the Coalition registry. Publishers earn revenue share when AI companies license content containing their signed text via the Coalition (60/40 split).

Enable Coalition enrollment in **Encypher → Settings → Coalition Auto-Enrollment**.
