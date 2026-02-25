# TEAM_232 — Free-Tier Batch Signing with Priority Queue

## Status: COMPLETE

## Objective
Allow free-tier users to access /batch/sign and /batch/verify endpoints using module-level
asyncio semaphores for cross-request priority (2 workers for free, 8 for enterprise).

## Tasks
- [x] 1.0 Add BATCH_WORKER_LIMITS to tier_config.py -- pytest
- [x] 2.0 Set BATCH_OPERATIONS quota to -1 for FREE in quota.py -- pytest
- [x] 3.0 Add module-level semaphores + update _run_workers in batch_service.py -- pytest
- [x] 4.0 Remove bulk_operations_enabled gate from batch.py -- pytest
- [x] 5.0 Update tests in test_batch_endpoints.py -- 6/6 pass
- [x] 6.0 Run full test suite -- 1262 pass, 2 pre-existing failures unrelated to batch

## Handoff Notes
All changes complete. Two pre-existing test failures unrelated to batch:
- test_rights_crawler_analytics.py::TestEnhancedCrawlerSummary::test_enhanced_crawler_summary_has_compliance_fields (MagicMock issue)
- test_sign_advanced_composed_org_missing_bootstraps_and_auto_provisions_key (real DB dependency)

## Suggested commit message
feat(batch): allow free-tier access to /batch/sign and /batch/verify

- Remove bulk_operations_enabled enterprise gate from batch router
- Set BATCH_OPERATIONS quota to -1 for Free (C2PA_SIGNATURES 1k/mo is the real constraint)
- Add module-level asyncio semaphores: Free=2 workers, Enterprise=8 workers
  so Enterprise is never starved by Free batch traffic
- Add BATCH_WORKER_LIMITS dict + get_batch_worker_limit() to tier_config.py
- Update tests: free tier now expects 200 (not 403) for multi-item batches
- Add test: free tier still gets 400 for single-item batch
