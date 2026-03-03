# Email Embedding Survivability Matrix

This matrix summarizes expected behavior for Encypher embedding families when content is processed by common email pipeline transformations.

## Embedding families compared

- **micro (VS256-RS)** -- `manifest_mode=micro, ecc=true, legacy_safe=false`
  - Per-segment RS-protected VS256 marker (`44` invisible chars)
  - Full C2PA wrapper at document level (when `embed_c2pa=true`)
  - Strong against partial corruption when VS payload survives
  - Not Word-safe -- Variation Selectors render as box glyphs in Word

- **micro (legacy_safe_rs)** -- `manifest_mode=micro, ecc=true, legacy_safe=true`
  - Per-segment RS-protected base-6 marker (`112` invisible chars)
  - Uses 6 confirmed Word-safe chars (ZWNJ/ZWJ/CGJ/MVS/LRM/RLM)
  - Vulnerable to aggressive format-control stripping

## Simulated processor transforms

| Transform | Description | micro VS256-RS | micro legacy_safe_rs |
|---|---|---:|---:|
| identity | No modifications | survives | survives |
| unicode_nfc | Unicode NFC normalization | survives | survives |
| strip_supplementary_vs | Remove VS17-VS256 | usually breaks | survives |
| strip_all_variation_selectors | Remove all variation selectors | breaks | survives |
| strip_format_controls | Remove format-control zero-widths | likely survives | breaks |

## Practical interpretation

No single invisible encoding is universally robust through every email path:

1. Pipelines that sanitize **variation selectors** harm `micro VS256-RS`.
2. Pipelines that sanitize **format-control zero-widths** harm `micro legacy_safe_rs`.
3. RS in both modes helps recover from partial corruption but cannot recover if all chars are removed.

## Suggested strategy

- **Default policy**: `micro VS256-RS` (`ecc=true, legacy_safe=false`) for compactness and error correction.
- **Fallback policy**: auto-switch to `micro legacy_safe_rs` (`ecc=true, legacy_safe=true`) for domains/processors observed to strip supplementary VS.
- **Verification policy**: always attempt both marker detectors during verification fallback logic.
- **Telemetry policy**: log processor/domain survivability outcomes and adapt routing by empirical evidence.

## Test sources

- `integrations/outlook-email-addin/tests/survivability-harness.test.js`
- `enterprise_api/tests/test_email_embedding_survivability.py`
