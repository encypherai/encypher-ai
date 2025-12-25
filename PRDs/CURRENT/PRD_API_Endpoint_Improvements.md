# PRD: Enterprise API Endpoint Improvements

**Status:** 🟢 Complete  
**Current Goal:** All endpoints implemented, tests written  
**Team:** TEAM_032

---

## Overview

This PRD addresses critical gaps in the Enterprise API that enterprise customers expect. Based on a customer-perspective review, we identified missing self-service capabilities for API key management, document listing, account information, and event webhooks. These are table-stakes features that competitors offer and are blocking enterprise sales.

---

## Objectives

- Enable programmatic API key management (create, rotate, revoke)
- Provide document listing and search capabilities
- Add account/organization info endpoint
- Implement webhook system for event notifications
- Improve endpoint naming clarity
- Maintain backward compatibility with existing integrations

---

## Success Criteria

- [ ] All new endpoints pass unit and integration tests
- [ ] OpenAPI documentation is complete with examples
- [ ] Existing endpoints continue to work (no breaking changes)
- [ ] Rate limiting and quota enforcement on new endpoints
- [ ] Admin endpoints hidden from public /docs

---

## Tasks

### 1.0 Account & Organization Endpoints

- [x] 1.1 Create account router (`app/routers/account.py`)
- [x] 1.2 Implement `GET /api/v1/account` - Get organization info, tier, features
- [x] 1.3 Implement `GET /api/v1/account/quota` - Detailed quota breakdown
- [x] 1.4 Write tests for account endpoints

### 2.0 Document Management Endpoints

- [x] 2.1 Create documents router (`app/routers/documents.py`)
- [x] 2.2 Implement `GET /api/v1/documents` - List signed documents (paginated)
- [x] 2.3 Implement `GET /api/v1/documents/{id}` - Get document details
- [x] 2.4 Implement `GET /api/v1/documents/{id}/history` - Get audit trail
- [x] 2.5 Implement `DELETE /api/v1/documents/{id}` - Soft delete with revocation
- [x] 2.6 Write tests for document endpoints

### 3.0 API Key Management Endpoints

- [x] 3.1 Create keys router (`app/routers/keys.py`)
- [x] 3.2 Implement `GET /api/v1/keys` - List API keys (masked)
- [x] 3.3 Implement `POST /api/v1/keys` - Create new API key
- [x] 3.4 Implement `DELETE /api/v1/keys/{id}` - Revoke API key
- [x] 3.5 Implement `POST /api/v1/keys/{id}/rotate` - Rotate API key
- [x] 3.6 Implement `PATCH /api/v1/keys/{id}` - Update key name/permissions
- [x] 3.7 Write tests for key management endpoints

### 4.0 Webhook System

- [x] 4.1 Create webhook database model (`app/models/webhook.py`)
- [x] 4.2 Create webhook router (`app/routers/webhooks.py`)
- [x] 4.3 Implement `POST /api/v1/webhooks` - Register webhook
- [x] 4.4 Implement `GET /api/v1/webhooks` - List webhooks
- [x] 4.5 Implement `DELETE /api/v1/webhooks/{id}` - Remove webhook
- [x] 4.6 Implement `POST /api/v1/webhooks/{id}/test` - Test webhook
- [x] 4.7 Create webhook dispatcher service (`app/services/webhook_dispatcher.py`)
- [x] 4.8 Integrate webhook events into signing/verification flows
- [x] 4.9 Write tests for webhook system

### 5.0 Endpoint Naming Improvements

- [x] 5.1 Add `/provenance/lookup` alias for `/lookup`
- [x] 5.2 Add `/enterprise/sign/advanced` alias for `/enterprise/embeddings/encode-with-embeddings`
- [ ] 5.3 Update OpenAPI descriptions for clarity
- [ ] 5.4 Ensure backward compatibility with old endpoint names

### 6.0 Documentation & Testing

- [ ] 6.1 Add OpenAPI examples for all new endpoints
- [ ] 6.2 Update SDK documentation
- [ ] 6.3 Create integration test suite
- [ ] 6.4 Performance test new endpoints

---

## API Specifications

### GET /api/v1/account

**Description:** Get current organization information, tier, and feature flags.

**Response:**
```json
{
  "success": true,
  "data": {
    "organization_id": "org_abc123",
    "name": "Acme Corp",
    "email": "admin@acme.com",
    "tier": "professional",
    "features": {
      "merkle_enabled": false,
      "byok_enabled": false,
      "sentence_tracking": true,
      "bulk_operations": false,
      "custom_assertions": false
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### GET /api/v1/documents

**Description:** List signed documents with pagination and filtering.

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 50, max: 100)
- `search` (string, optional) - Search in title
- `status` (string, optional) - "active", "revoked"
- `from_date` (ISO date, optional)
- `to_date` (ISO date, optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "document_id": "doc_abc123",
        "title": "Press Release Q4",
        "status": "active",
        "signed_at": "2024-12-20T15:30:00Z",
        "verification_url": "https://api.encypherai.com/api/v1/verify/doc_abc123"
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 50,
    "total_pages": 3
  }
}
```

### GET /api/v1/keys

**Description:** List API keys for the organization (keys are masked).

**Response:**
```json
{
  "success": true,
  "data": {
    "keys": [
      {
        "id": "key_abc123",
        "name": "Production Key",
        "prefix": "ek_live_abc1",
        "permissions": ["sign", "verify"],
        "created_at": "2024-06-01T10:00:00Z",
        "last_used_at": "2024-12-23T18:00:00Z",
        "is_active": true
      }
    ],
    "total": 3
  }
}
```

### POST /api/v1/keys

**Description:** Create a new API key.

**Request:**
```json
{
  "name": "CI/CD Pipeline Key",
  "permissions": ["sign", "verify"],
  "expires_in_days": 365
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "key_xyz789",
    "name": "CI/CD Pipeline Key",
    "key": "ek_live_xyz789abcdef...",
    "prefix": "ek_live_xyz7",
    "permissions": ["sign", "verify"],
    "created_at": "2024-12-23T20:30:00Z",
    "expires_at": "2025-12-23T20:30:00Z"
  },
  "warning": "Store this key securely. It will not be shown again."
}
```

### POST /api/v1/webhooks

**Description:** Register a webhook endpoint.

**Request:**
```json
{
  "url": "https://acme.com/webhooks/encypher",
  "events": ["document.signed", "document.revoked", "quota.warning"],
  "secret": "whsec_optional_shared_secret"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "wh_abc123",
    "url": "https://acme.com/webhooks/encypher",
    "events": ["document.signed", "document.revoked", "quota.warning"],
    "created_at": "2024-12-23T20:30:00Z",
    "is_active": true
  }
}
```

---

## Completion Notes

*To be filled upon completion*

---

## References

- Customer API Review: `.teams/TEAM_032_api_review.md`
- Existing API: `enterprise_api/app/routers/`
- Database Models: `enterprise_api/app/models/`
