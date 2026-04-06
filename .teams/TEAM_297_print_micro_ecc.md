# TEAM_297 - Print-Survivable Micro ECC Codec

**Status**: COMPLETE
**Started**: 2026-04-06
**Scope**: New print-survivable provenance embedding using 4-symbol space-width encoding with Reed-Solomon ECC, carrying the same log_id + HMAC payload as VS256-RS digital markers.

## Session Log

### Session 1 (2026-04-06)
- Read existing codecs: print_stego.py, vs256_rs_crypto.py, legacy_safe_crypto.py
- Mapped signing/verification integration points
- Created PRD at PRDs/CURRENT/PRD_Print_Micro_ECC.md
- Implemented core codec: app/utils/print_micro_ecc.py
  - 4-symbol base-4 encoding (hair, six-per-em, thin, regular space)
  - RS(48,32) error correction (16 parity, corrects 8 unknown errors)
  - Interleaved position selection for burst-error resilience
  - HMAC construction matching VS256-RS format
- Wrote 32 unit tests (tests/test_print_micro_ecc.py) - all passing
- Wrote 27 simulation tests (tests/test_print_micro_ecc_simulation.py) - all passing
  - Font rendering verification at 150/300/600 DPI
  - Noise sweep characterizing operating envelope
  - Burst error resilience (30 contiguous spaces recovered)
- Wired into signing pipeline (signing.py, sign_schemas.py)
- Wired into verification pipeline (unified_verify_service.py, verify_schemas.py)
- Added feature definition (api_response.py)
- Enforced mutual exclusion with enable_print_fingerprint
- All 70 tests passing (11 existing + 32 unit + 27 simulation)
- Lint clean (ruff)

## Key Findings

### Operating Envelope
- Perfect recovery at 150/300/600 DPI with no noise
- Recovers with RS at 0.01em noise (4 byte errors, within 8-error capacity)
- Fails at 0.015em noise (11 byte errors > 8 limit)
- Bottleneck: thin-to-six-per-em gap (0.033 em) is tightest decision boundary

### Design Decision: RS(48,32) vs RS(40,32)
Doubled parity (16 vs 8 symbols) for print-channel robustness. Costs 192 positions
(~193 words min) instead of 160, but provides comfortable margin at realistic
institutional print/scan noise levels.

## Suggested Commit Message

```
feat(TEAM_297): add print-survivable micro ECC provenance embedding

Implement 4-symbol space-width codec (hair/six-per-em/thin/regular) with
RS(48,32) error correction for print-survivable provenance. Carries the
same log_id + HMAC payload as VS256-RS digital markers, enabling unified
transparency log resolution from both digital and printed documents.

- Core codec: app/utils/print_micro_ecc.py (base-4, RS ECC, interleaving)
- 32 unit tests + 27 digital print simulation tests (all passing)
- Pipeline integration: enable_print_micro_ecc in sign/verify options
- Enterprise tier gate with mutual exclusion vs print_fingerprint
- Simulation shows reliable recovery up to 0.01em noise at 300-600 DPI
```
