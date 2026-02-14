# Email Embedding Survivability Matrix

This matrix summarizes expected behavior for Encypher embedding families when content is processed by common email pipeline transformations.

## Embedding families compared

- **micro_ecc_c2pa**
  - Per-segment RS-protected VS256 marker (`44` invisible chars)
  - Full C2PA wrapper at document level
  - Strong against partial corruption when VS payload survives
- **zw_embedding**
  - Base-4 zero-width marker (`132` chars)
  - Uses Word-safe chars (ZWNJ/ZWJ/CGJ/MVS)
  - Vulnerable to aggressive format-control stripping

## Simulated processor transforms

| Transform | Description | micro_ecc_c2pa | zw_embedding |
|---|---|---:|---:|
| identity | No modifications | ✅ survives | ✅ survives |
| unicode_nfc | Unicode NFC normalization | ✅ survives | ✅ survives |
| strip_supplementary_vs | Remove VS17–VS256 | ❌ usually breaks | ✅ survives |
| strip_all_variation_selectors | Remove all variation selectors | ❌ breaks | ✅ survives |
| strip_format_controls | Remove format-control zero-widths | ✅ likely survives | ❌ breaks |

## Practical interpretation

No single invisible encoding is universally robust through every email path:

1. Pipelines that sanitize **variation selectors** harm `micro_ecc_c2pa`.
2. Pipelines that sanitize **format-control zero-widths** harm `zw_embedding`.
3. RS in `micro_ecc_c2pa` helps recover from partial corruption but cannot recover if all VS are removed.

## Suggested strategy

- **Default policy**: `micro_ecc_c2pa` for compactness and error correction.
- **Fallback policy**: auto-switch to `zw_embedding` for domains/processors observed to strip supplementary VS.
- **Verification policy**: always attempt both marker detectors during verification fallback logic.
- **Telemetry policy**: log processor/domain survivability outcomes and adapt routing by empirical evidence.

## Test sources

- `integrations/outlook-email-addin/tests/survivability-harness.test.js`
- `enterprise_api/tests/test_email_embedding_survivability.py`
