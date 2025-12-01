# PRD: Bitstring Status Lists for Document Revocation

## Status: In Progress
## Current Goal: Implement per-document revocation at internet scale

---

## Overview

Implement W3C-compatible Bitstring Status Lists to enable per-document revocation for the Enterprise API. This system will support 10+ billion documents with O(1) status lookups, enabling publishers like NYT to revoke individual articles without affecting their entire signing certificate.

---

## Objectives

- Enable per-document revocation without certificate-level impact
- Support 10+ billion documents across all publishers
- Achieve <5 minute revocation propagation via CDN caching
- Maintain O(1) verification performance with cached bitstrings
- Provide W3C StatusList2021 compatibility for interoperability
- Add revocation API for publisher self-service

---

## Tasks

### 1.0 Database Layer
- [x] 1.1 Design data models for status tracking
- [x] 1.2 Create `StatusListEntry` model — ✅ app/models/status_list.py
- [x] 1.3 Create `StatusListMetadata` model — ✅ app/models/status_list.py
- [x] 1.4 Create Alembic migration — ✅ alembic/versions/20251201_110000_add_status_lists.py
- [x] 1.5 Add indexes for efficient queries — ✅ included in migration

### 2.0 Status Allocation (Signing)
- [x] 2.1 Create `StatusService` class — ✅ app/services/status_service.py
- [x] 2.2 Implement `allocate_status_index()` for new documents — ✅ status_service.py
- [x] 2.3 Integrate with `embedding_service.py` to add status assertion — ✅ embedding_service.py
- [ ] 2.4 Update manifest structure with status reference (in C2PA assertions)

### 3.0 Status List Generation
- [x] 3.1 Create background worker for bitstring generation — ✅ status_service.generate_status_list()
- [x] 3.2 Implement gzip + base64 encoding per W3C spec — ✅ status_service.py
- [x] 3.3 Build StatusList2021Credential JSON structure — ✅ status_service.py
- [ ] 3.4 Add CDN upload functionality (S3/R2 compatible) — deferred to production

### 4.0 Verification Integration
- [x] 4.1 Create `check_revocation()` in StatusService — ✅ status_service.py
- [x] 4.2 Add status list caching with TTL — ✅ status_service._list_cache
- [x] 4.3 Integrate into `verification_logic.py` — ✅ verification_logic.py
- [x] 4.4 Add `DOC_REVOKED` reason code — ✅ verification_logic.py

### 5.0 Revocation API
- [x] 5.1 Create `/api/v1/status/documents/{id}/revoke` endpoint — ✅ routers/status.py
- [x] 5.2 Create `/api/v1/status/documents/{id}/reinstate` endpoint — ✅ routers/status.py
- [x] 5.3 Create `/api/v1/status/list/{org}/{index}` public endpoint — ✅ routers/status.py
- [x] 5.4 Add audit logging for revocation actions — ✅ via StatusListEntry fields

### 6.0 Documentation
- [x] 6.1 Update enterprise_api README.md — ✅ Added revocation endpoints, features, architecture
- [x] 6.2 Add status list documentation — ✅ Included in README
- [x] 6.3 Update API reference with new endpoints — ✅ Added to endpoint tables

### 7.0 Testing
- [x] 7.1 Unit tests for StatusService — ✅ tests/test_status_service.py
- [ ] 7.2 Integration tests for revocation flow
- [ ] 7.3 Performance tests for bitstring operations

---

## Success Criteria

- [x] Documents can be revoked individually via API — ✅ POST /status/documents/{id}/revoke
- [x] Revoked documents fail verification with `DOC_REVOKED` code — ✅ verification_logic.py
- [ ] Status lists are served from CDN with <100ms latency — requires production deployment
- [x] System handles 10B+ document capacity — ✅ 131K docs/list, unlimited lists
- [x] Unit tests pass — ✅ test_status_service.py
- [x] README updated with new features — ✅ comprehensive documentation added

---

## Technical Specifications

### Bitstring Format
- 131,072 bits per list (16,384 bytes)
- Gzip compressed (~2-4 KB typical)
- Base64 encoded for JSON transport
- W3C StatusList2021 credential wrapper

### Sharding Strategy
- Primary key: (organization_id, list_index, bit_index)
- New list created when current list reaches capacity
- Sequential allocation within organization

### CDN Configuration
- Cache-Control: public, max-age=300 (5 minutes)
- Content-Type: application/json
- Path: /status/{organization_id}/{list_index}.json

---

## Completion Notes

(To be filled upon completion)
