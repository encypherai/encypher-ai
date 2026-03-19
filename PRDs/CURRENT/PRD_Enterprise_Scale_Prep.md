# PRD: Enterprise Scale Preparation

**Status:** Complete
**Current Goal:** All items implemented
**Team:** TEAM_259

## Overview
Address scaling issues and add remaining features identified in the enterprise rollout gap analysis. SDK publishing CI/CD already exists -- focus is on fixing the OpenAPI generation that feeds it.

## Tasks

### H3: Stripe Connect Account DB Storage

- [x] 1.0 Stripe Connect Account Storage -- pytest 10/10
  - [x] 1.1 Add StripeConnectAccount model to billing-service models
  - [x] 1.2 Add Alembic migration for connect_accounts table
  - [x] 1.3 Refactor endpoint to store/lookup connect_account_id locally
  - [x] 1.4 Update webhook handler for account.updated events
  - [x] 1.5 Tests (10 tests)

### P2.1: CDN Provenance Analytics Dashboard

- [x] 2.0 CDN Analytics Dashboard -- tsc clean
  - [x] 2.1 Add api.ts methods for /cdn/analytics/summary and /cdn/analytics/timeline
  - [x] 2.2 Create /cdn-analytics/page.tsx with summary cards and timeline chart
  - [x] 2.3 Add navigation entry in DashboardLayout
  - [x] 2.4 Enterprise tier gate

### P3.5: OpenAPI Spec Auto-Generation Fix

- [x] 3.0 OpenAPI Generation Fix
  - [x] 3.1 Fix broken import (_filter_openapi_for_public moved to app.bootstrap.docs)
  - [x] 3.2 Fix path collision to skip duplicates instead of raising RuntimeError
  - [x] 3.3 Fix _rewrite_refs scope to only rewrite new paths
  - [x] 3.4 Regenerate all specs cleanly (166 public / 209 schemas)
  - [x] 3.5 Validate Python SDK generates and compiles

### P3.1: Webhook DLQ + Retry

- [x] 4.0 Webhook Retry Mechanism -- pytest 10/10
  - [x] 4.1 Implement retry logic with exponential backoff (60s/300s/900s)
  - [x] 4.2 Populate next_retry_at on failed deliveries
  - [x] 4.3 Background task (30s poll) to process pending retries
  - [x] 4.4 Mark as permanently_failed after max_attempts (DLQ)
- [x] 5.0 Webhook DLQ Dashboard UI -- tsc clean
  - [x] 5.1 Add delivery history panel (expandable per webhook)
  - [x] 5.2 Add api.ts methods for deliveries + manual retry
  - [x] 5.3 Manual retry button for failed deliveries
  - [x] 5.4 Status badges (success/retrying/permanently_failed)

## Completion Notes
Completed 2026-03-19 by TEAM_259. 20 new tests (10 Connect + 10 webhook retry). Dashboard builds clean. OpenAPI generation now automated.
