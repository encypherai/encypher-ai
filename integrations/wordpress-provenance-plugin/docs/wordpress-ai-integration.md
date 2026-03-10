# WordPress/ai Integration Guide

## Overview

Encypher integrates with the [WordPress/ai plugin](https://github.com/WordPress/ai) to automatically embed C2PA-compatible provenance into AI-generated content. This makes Encypher a natural part of the WordPress AI Building Blocks story.

## Architecture

```
WordPress/ai (AI Experiments)
  └── Title Generation ──────────┐
  └── Excerpt Generation ─────────┤
  └── Summarization ──────────────┤──→ Encypher Compatibility Layer ──→ /api/v1/sign
  └── Review Notes ───────────────┤                                         ↓
  └── Alt Text ───────────────────┘                          Signed text returned to experiment
                                                                         ↓
                                                              Embedded in WordPress post
```

## Components

### 1. Compatibility Layer (`class-encypher-provenance-wordpress-ai.php`)
Detects WordPress/ai and hooks into all experiment output filters. Calls Encypher's `/api/v1/sign` endpoint on each piece of AI-generated content.

### 2. Abilities Registration (`class-encypher-sign-ability.php`, `class-encypher-verify-ability.php`)
Registers `encypher/sign` and `encypher/verify` as first-class WordPress Abilities. Any plugin can call:
```php
$signed = wp_do_ability('encypher/sign', ['text' => $ai_content, 'metadata' => $context]);
$provenance = wp_do_ability('encypher/verify', ['text' => $signed_content]);
```

### 3. Gutenberg Sidebar Panel (`assets/js/wordpress-ai-provenance.js`)
Adds an "AI Content Provenance" panel in the block editor showing:
- Shield badge: green (verified) / yellow (unverified) / red (tampered)
- List of signed experiments
- "Check Provenance" button

### 4. Coalition Auto-Enrollment
When enabled in settings, automatically enrolls the WordPress site in the Encypher Coalition when the integration is activated. Coalition members earn revenue share when AI companies license signed content.

## Setup

1. Install and activate the Encypher Provenance plugin
2. Install and activate the WordPress/ai plugin
3. Go to **Encypher → Settings**
4. Enter your Encypher API key ([get one free](https://encypherai.com))
5. Enable **WordPress/ai Integration**
6. Optionally enable **Coalition Auto-Enrollment**
7. Go to WordPress/ai settings and enable desired experiments

## Verification

After setup, any AI-generated content will carry Encypher provenance. Verify:

```bash
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "Your signed content here"}'
```

## Upstream PR

See `docs/experiments/content-provenance.md` for the upstream PR draft for the WordPress/ai repository.

## License

GPL-2.0-or-later (matching WordPress/ai)
