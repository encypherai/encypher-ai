# PRD: API Access Gating

**Status**: Complete
**Team**: TEAM_006
**Current Goal**: Implement user approval flow for API access

---

## Overview

Implement an industry-standard API access gating system where users must request and be approved for API access before they can generate API keys. This enables controlled rollout during preview/beta phases and ensures quality early adopters.

---

## Objectives

- Gate API key generation behind an approval workflow
- Provide clear UX for users to request access
- Enable admins to approve/deny access requests
- Support audit trail for access decisions
- Clean up dead `/pitch` middleware from marketing site

---

## Tasks

### 1.0 Backend - Auth Service

- [x] 1.1 Add `api_access_status` enum to User model — ✅ pytest
  - [x] 1.1.1 Write unit tests for new field behavior
  - [x] 1.1.2 Add field to `app/db/models.py`
  - [x] 1.1.3 Create Alembic migration `003_api_access_gating.py`

- [x] 1.2 Add API endpoints — ✅ pytest
  - [x] 1.2.1 `POST /api/v1/auth/request-api-access` - User requests access
  - [x] 1.2.2 `GET /api/v1/auth/api-access-status` - Check current status
  - [x] 1.2.3 `POST /api/v1/admin/approve-api-access` - Admin approves
  - [x] 1.2.4 `POST /api/v1/admin/deny-api-access` - Admin denies
  - [x] 1.2.5 `GET /api/v1/admin/pending-access-requests` - List pending
  - [x] 1.2.6 `GET /api/v1/admin/check-api-access/{user_id}` - Check if approved

- [x] 1.3 Add Pydantic schemas for request/response

### 2.0 Frontend - Dashboard

- [x] 2.1 API Access Status Component — ✅ done
  - [x] 2.1.1 Show current status (pending/approved/denied)
  - [x] 2.1.2 Request access form with use case description
  - [x] 2.1.3 Success/pending state after request

- [x] 2.2 Gate API Key Generation — ✅ done
  - [x] 2.2.1 Check `api_access_status` before showing key generation
  - [x] 2.2.2 Show "Request Access" CTA for non-approved users

- [x] 2.3 Admin Dashboard — ✅ done
  - [x] 2.3.1 Super admin check via API
  - [x] 2.3.2 Pending requests list with approve/deny buttons
  - [x] 2.3.3 Default super admin: erik.svilich@encypher.com

### 3.0 Cleanup

- [x] 3.1 Remove dead `/pitch` middleware from marketing site — ✅ done

---

## Success Criteria

- [x] Users cannot generate API keys without approved status
- [x] Users can request access with a use case description
- [x] Admins can approve/deny requests via API and dashboard
- [x] Super admin role enforced (erik.svilich@encypher.com)
- [x] All tests pass (`uv run pytest`)
- [ ] Dashboard correctly shows access status

---

## Technical Design

### User Model Addition

```python
class ApiAccessStatus(str, Enum):
    NOT_REQUESTED = "not_requested"  # Default for new users
    PENDING = "pending"              # User requested, awaiting review
    APPROVED = "approved"            # Admin approved
    DENIED = "denied"                # Admin denied

class User(Base):
    # ... existing fields ...
    api_access_status = Column(String(32), default="not_requested")
    api_access_requested_at = Column(DateTime(timezone=True), nullable=True)
    api_access_decided_at = Column(DateTime(timezone=True), nullable=True)
    api_access_decided_by = Column(String(64), nullable=True)  # Admin user_id
    api_access_use_case = Column(Text, nullable=True)  # User's stated use case
```

### API Endpoints

```
POST /api/v1/auth/request-api-access
  Body: { "use_case": "Building a content verification tool..." }
  Response: { "status": "pending", "message": "Request submitted" }

GET /api/v1/auth/api-access-status
  Response: { "status": "pending|approved|denied|not_requested" }

POST /api/v1/admin/approve-api-access
  Body: { "user_id": "user_abc123" }
  Response: { "status": "approved" }

POST /api/v1/admin/deny-api-access
  Body: { "user_id": "user_abc123", "reason": "..." }
  Response: { "status": "denied" }

GET /api/v1/admin/pending-access-requests
  Response: { "requests": [...] }
```

---

## Completion Notes

(To be filled upon completion)
