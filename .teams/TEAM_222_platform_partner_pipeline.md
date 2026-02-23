# TEAM_222 - Platform Partner Publisher Pipeline

## Session Status: COMPLETE

## Goal
Implement the Freestar/platform partner pipeline:
1. Proxy signing via `/sign` with `publisher_org_id` field
2. Bulk publisher provisioning endpoint
3. `news_publisher_default` template zero-config defaults
4. Partner-branded publisher claim email + claim flow

## Tasks

- [x] Step 1: Add `notice_status` + `coalition_member` to news_publisher_default template
- [x] Step 2: Add `publisher_org_id` field to UnifiedSignRequest schema
- [x] Step 3: Add proxy signing logic to signing.py router
- [x] Step 4: Add bulk-provision endpoint to auth-service organizations.py
- [x] Step 5a: Add `bulk_provision_publishers()` to auth_service_client.py
- [x] Step 5b: Create enterprise_api/app/routers/partner.py
- [x] Step 5c: Register partner router in main.py
- [x] Step 6a: Add TestProxySigning + TestBulkProvision to test_platform_partner.py -- pytest 17 passed
- [x] Step 6b: Create services/auth-service/tests/test_bulk_provision.py -- pytest 8 passed
- [x] Step 7: Add strategic_partner demo key to DEMO_KEYS in dependencies.py

## Test Results
- enterprise_api: 1226 passed (1 pre-existing failure in test_sdk_openapi_public_artifact.py)
- auth-service: 219 passed
- mypy: clean on new files

## Files Changed
- enterprise_api/app/core/rights_templates.py -- added notice_status, coalition_member to news_publisher_default
- enterprise_api/app/schemas/sign_schemas.py -- added publisher_org_id to UnifiedSignRequest
- enterprise_api/app/routers/signing.py -- proxy signing block + auth_service_client import
- enterprise_api/app/services/auth_service_client.py -- added bulk_provision_publishers()
- enterprise_api/app/routers/partner.py (NEW) -- bulk provisioning endpoint + claim email
- enterprise_api/app/main.py -- registered partner router
- enterprise_api/app/config.py -- added notification_service_url, dashboard_url
- enterprise_api/app/dependencies.py -- added strategic_partner demo key to DEMO_KEYS
- enterprise_api/README.md -- added /partner/publishers/provision to endpoint table
- enterprise_api/tests/test_platform_partner.py -- added TestProxySigning, TestBulkProvision
- services/auth-service/app/api/v1/organizations.py -- bulk-provision schemas + endpoint
- services/auth-service/tests/test_bulk_provision.py (NEW) -- 8 tests

## Suggested Git Commit Message
```
feat(partner): platform partner publisher pipeline (TEAM_222)

- Add proxy signing via publisher_org_id on POST /sign (strategic_partner tier)
  - Publisher's quota, rate limits, rights profile, and webhooks are used
  - partner_org_id and publisher_org_id injected into successful response
- Add POST /api/v1/partner/publishers/provision for bulk publisher onboarding
  - Creates orgs + invitations via auth-service internal endpoint
  - Creates rights profiles with notice_status=active, coalition_member=True
  - Sends partner-branded claim email per provisioned publisher
- Add /organizations/internal/bulk-provision to auth-service (internal endpoint)
  - Creates org without owner + owner-role invitation per publisher
  - Domain claim attempted if domain provided (failure non-fatal)
- Add notice_status=active and coalition_member=True defaults to news_publisher_default template
- Add strategic_partner demo key to DEMO_KEYS for testing
- Add notification_service_url and dashboard_url to enterprise_api config
- Tests: 17 enterprise_api tests, 8 auth-service tests, all passing
```
