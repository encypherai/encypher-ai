# Enterprise API Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `E_RATE_SIGN` | 429 | Signing requests exceeded per-minute quota |
| `E_RATE_BATCH_SIGN` | 429 | Batch signing exceeded quota |
| `E_RATE_BATCH_VERIFY` | 429 | Batch verification exceeded quota |
| `E_RATE_STREAM` | 429 | Streaming signing exceeded quota |
| `E_BATCH_TOO_LARGE` | 400 | Batch payload exceeded allowed size |
| `E_IDEMPOTENCY_MISMATCH` | 409 | Idempotency key reused with different payload |
| `E_IDEMPOTENT_REPLAY` | 409 | Idempotency cache rejected the request |
| `E_BATCH_ITEM` | 500 | Batch item failed unexpectedly |
| `E_VERIFY_TAMPERED` | 200 | Verification completed but content was tampered |
| `E_STREAM_SIGN` | 500 | Streaming signer failed |

See `enterprise_api/middleware/api_rate_limiter.py` for quota defaults and `enterprise_api/app/routers` for endpoint-specific handling.
