# Enterprise Bulk Jobs API (Async Signing + Import/Export)

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Decide job queue architecture and artifact storage approach.

## Overview

Enterprise publishers need to sign large archives (10K–10M documents) without blocking editorial systems. This PRD defines an async Jobs API for bulk signing, bulk verification, and bulk export with progress tracking, retries, and webhook callbacks.

## Objectives

- Provide asynchronous bulk signing and verification workflows
- Support standard ingest formats (JSONL/CSV/ZIP/S3 URL)
- Provide robust job status/progress tracking and downloadable results
- Support idempotency, retries, cancellation, and auditing
- Ensure tier-based limits (concurrency, throughput, retention)

## Tasks

### 1.0 Architecture & Requirements

- [ ] 1.1 Select job system
  - [ ] 1.1.1 Redis + RQ/Celery
  - [ ] 1.1.2 Postgres-backed queue (if avoiding Redis)
  - [ ] 1.1.3 Cloud queue option (SQS) for enterprise deployments
- [ ] 1.2 Define job types
  - [ ] 1.2.1 `bulk.sign`
  - [ ] 1.2.2 `bulk.verify`
  - [ ] 1.2.3 `bulk.export`
- [ ] 1.3 Define artifacts storage
  - [ ] 1.3.1 Store input/output in object storage (S3 compatible)
  - [ ] 1.3.2 Signed URL generation for download
  - [ ] 1.3.3 Retention policy by tier
- [ ] 1.4 Define security requirements
  - [ ] 1.4.1 Enforce org isolation on all job endpoints
  - [ ] 1.4.2 Prevent SSRF for URL-based inputs
  - [ ] 1.4.3 Validate file types and size limits

### 2.0 Data Model

- [ ] 2.1 Create Job table/model
  - [ ] 2.1.1 `id`, `organization_id`, `job_type`, `status`
  - [ ] 2.1.2 `total_items`, `processed_items`, `failed_items`
  - [ ] 2.1.3 `input_uri`, `output_uri`, `error_uri`
  - [ ] 2.1.4 `created_at`, `started_at`, `completed_at`
  - [ ] 2.1.5 `webhook_url`, `webhook_secret_id`
  - [ ] 2.1.6 `idempotency_key` (optional)
- [ ] 2.2 Create JobItem table/model (optional, if per-item tracking is required)
  - [ ] 2.2.1 `job_id`, `item_index`, `status`, `error`, `result_ref`

### 3.0 API Endpoints

- [ ] 3.1 Create `POST /api/v1/jobs/bulk-sign`
  - [ ] 3.1.1 Accept upload (JSONL/CSV/ZIP) or `input_url`
  - [ ] 3.1.2 Validate payload and create job
  - [ ] 3.1.3 Return `job_id` and status URL
- [ ] 3.2 Create `POST /api/v1/jobs/bulk-verify`
- [ ] 3.3 Create `POST /api/v1/jobs/bulk-export`
- [ ] 3.4 Create `GET /api/v1/jobs/{job_id}`
- [ ] 3.5 Create `GET /api/v1/jobs/{job_id}/results`
- [ ] 3.6 Create `GET /api/v1/jobs/{job_id}/errors`
- [ ] 3.7 Create `DELETE /api/v1/jobs/{job_id}` (cancel)
- [ ] 3.8 Add SSE progress endpoint
  - [ ] 3.8.1 `GET /api/v1/jobs/{job_id}/events`

### 4.0 Worker Implementation

- [ ] 4.1 Implement worker process
  - [ ] 4.1.1 Fetch input artifact
  - [ ] 4.1.2 Stream/process items
  - [ ] 4.1.3 Persist output artifact incrementally
- [ ] 4.2 Bulk sign worker
  - [ ] 4.2.1 Use org signing keys
  - [ ] 4.2.2 Apply consistent claim_generator/actions templates
- [ ] 4.3 Retry policy
  - [ ] 4.3.1 Per-item retries
  - [ ] 4.3.2 Job-level failure thresholds
- [ ] 4.4 Cancellation support

### 5.0 Webhooks

- [ ] 5.1 Implement webhook delivery
  - [ ] 5.1.1 Sign payloads (HMAC)
  - [ ] 5.1.2 Retries with exponential backoff
- [ ] 5.2 Implement webhook configuration UI in dashboard

### 6.0 Limits, Quotas, and Cost Controls

- [ ] 6.1 Define tier-based concurrency and throughput
- [ ] 6.2 Enforce max input size, max items per job
- [ ] 6.3 Enforce retention limits for artifacts

### 7.0 Testing & Validation

- [ ] 7.1 Unit tests passing — ✅ pytest
- [ ] 7.2 Integration tests passing — ✅ pytest
- [ ] 7.3 Load verification — ✅ benchmark

## Success Criteria

- Publishers can submit bulk jobs and retrieve results reliably
- Jobs can be cancelled and retried deterministically
- Webhook delivery is secure and dependable
- All tests passing with verification markers

## Completion Notes

(Filled when PRD is complete.)
