# PRD: Dashboard Usage Analytics + Activity Fix

**Status:** In Progress
**Current Goal:** Ensure usage analytics and activity timeline are driven by real metrics for local API key usage and remove demo placeholders.

## Overview
The dashboard Usage & Analytics page must display real usage metrics after API calls in the local full-stack setup. Demo placeholder data must be removed, and activity timeline entries must come from actual analytics-service events.

## Objectives
- Remove demo activity timeline content and load real activity events from analytics-service.
- Ensure usage metrics are emitted for verification/signing calls made with local API keys.
- Provide an analytics-service activity endpoint aligned with dashboard needs.
- Add tests covering activity feed sourcing and metrics emission path.

## Tasks
- [x] 1.0 Baseline verification
  - [x] 1.1 Run `uv run pytest services/analytics-service/tests/test_stream_consumer_parse_metric.py` ✅ pytest
  - [x] 1.2 Run `uv run pytest services/verification-service/tests/test_verify_api_key_auth.py` ✅ pytest

- [x] 2.0 Activity timeline real data
  - [x] 2.1 Add analytics-service activity endpoint + schema
  - [x] 2.2 Wire dashboard ActivityFeed to analytics API
  - [x] 2.3 Remove demo mock activity data

- [x] 3.0 Usage metrics emission for verification-service
  - [x] 3.1 Add metrics middleware + client in verification-service
  - [x] 3.2 Persist org/user context for optional API key verification

- [x] 3.3 Usage metrics emission for key-service
  - [x] 3.3.1 Add metrics middleware + client in key-service ✅ pytest
  - [x] 3.3.2 Persist org/user context on key generation/validation ✅ pytest
  - [x] 3.3.3 Add key-service metrics emission tests ✅ pytest

- [ ] 4.0 Tests (TDD)
  - [ ] 4.1 Add dashboard contract coverage to ensure no mock activity timeline data
  - [x] 4.2 Add analytics-service tests for activity feed mapping ✅ pytest

- [ ] 5.0 Verification
  - [ ] 5.1 Run `uv run pytest services/analytics-service/tests/test_stream_consumer_parse_metric.py` ✅ pytest
  - [ ] 5.2 Run `uv run pytest services/verification-service/tests/test_verify_api_key_auth.py` ✅ pytest
  - [ ] 5.3 Run `npm test` in `apps/dashboard` ✅
  - [ ] 5.4 Puppeteer verification for Usage & Analytics page ✅ puppeteer
  - [x] 5.5 Run `uv run ruff check .` ✅

## Success Criteria
- Usage & Analytics dashboard shows API usage after testing a local API key.
- Activity timeline displays real events or empty state without demo content.
- Metrics from verification-service are emitted to analytics stream when API key is supplied.
- Tests and verification steps pass.

## Completion Notes
- (Filled when PRD is complete.)
