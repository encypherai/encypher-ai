---
Title: Website Migration to Services and API Gateway (Security-First)
Author: Platform Engineering
Owners: Platform, Frontend, Security
Status: Draft
Last-Updated: 2025-11-05
Version: 1.0
---

# 1. Summary
Migrate the public website/backend usage from a monolithic FastAPI app to a services-based architecture with a thin API Gateway. Authentication is rebuilt from scratch with `services/auth-service`. Analytics flows are handled by `services/analytics-service` as the minimal dedicated backend for website and product metrics. Public verification flows are routed to `enterprise_api` through the gateway. Investor-access is excluded.

Security is the top priority: short-lived access tokens, httpOnly refresh cookies, strict CORS, input validation, structured logging with correlation IDs, and least-privilege data access.

# 2. Goals & Non-Goals
## 2.1 Goals
- Provide a single base URL for the frontend via API Gateway.
- Recreate user authentication using `auth-service` with security best practices.
- Instrument analytics using `analytics-service`; support optional anonymous pageviews (rate-limited) if required.
- Route public verification to `enterprise_api` via gateway without changing frontend paths.
- Remove reliance on legacy website backend for application features.

## 2.2 Non-Goals
- Investor-access user flows and admin tooling.
- Billing/subscriptions migration (future via `billing-service`).
- Complex service discovery or mesh in MVP; static routing is sufficient initially.

# 3. Stakeholders
- Engineering (Platform, Frontend, Security)
- Operations (DevOps/SRE)
- Product (Website/Dashboard Owners)

# 4. Background
- The website currently uses a monolithic backend. We are moving to microservices already present in `services/` (auth-service, analytics-service) and `enterprise_api` for public verification/streaming.
- The frontend relies on a single `NEXT_PUBLIC_API_BASE_URL` and should continue to do so via the API Gateway.

# 5. Assumptions
- Fresh authentication implementation—no legacy user DB migration necessary.
- Docker Compose for local development; production deployments via current CI/CD.
- Standard Response Format is used across services.

# 6. Functional Requirements
## 6.1 API Gateway (Port 8000)
- Routing:
  - `/api/v1/auth/*` → auth-service (8001)
  - `/api/v1/analytics/*` → analytics-service (8006)
  - `/api/v1/verify*` → enterprise_api verification endpoints
- CORS allowlist: `https://encypherai.com`, `https://www.encypherai.com`, `http://localhost:3000` (dev).
- Health: `GET /health` → `{ status, service, version }`.
- Metrics: `GET /metrics` (Prometheus).
- Logging: Structured JSON logs with correlation ID (`X-Request-ID`).

## 6.2 Authentication (auth-service via Gateway)
- Endpoints:
  - `POST /api/v1/auth/register` (email/password)
  - `POST /api/v1/auth/login` (email/password)
  - `POST /api/v1/auth/refresh` (httpOnly cookie; rotation)
  - `POST /api/v1/auth/logout` (revoke refresh token(s))
  - `POST /api/v1/auth/verify` (token introspection for downstream services)
- Responses conform to Standard Response Format. JWT claims include: `sub`, `email`, `roles`, `iss`, `aud`, `iat`, `exp`.
- Optional follow-ups (post-MVP): email verification, password reset.

## 6.3 Analytics (analytics-service via Gateway)
- `POST /api/v1/analytics/metrics` (Bearer token required; validated via `auth-service /verify`).
- `GET /api/v1/analytics/usage|services|timeseries|report` (Bearer token required).
- Optional: `POST /api/v1/analytics/pageview` public endpoint (strict rate-limit, minimal payload, bot filtering).

## 6.4 Public Verification (enterprise_api via Gateway)
- `GET /api/v1/verify*` is forwarded to enterprise_api public verify routes.
- Path compatibility is preserved for the frontend.

## 6.5 Frontend Updates
- NextAuth Credentials Provider → `POST {BASE_URL}/api/v1/auth/login`.
- Session stores `access_token` (and refresh workflow via httpOnly cookie endpoints on gateway/auth-service).
- Analytics events sent via `/api/v1/analytics/metrics` with Bearer token.

# 7. Non-Functional Requirements
- Availability: ≥99.9% for Gateway & Auth in production.
- Latency Targets: p95 <200ms (Gateway/Auth), <300ms (Analytics reads).
- Scalability: Stateless services; horizontal scale supported.
- Observability: Health, metrics, structured logs; trace/correlation IDs.
- Configuration hygiene: `.env.example` for all components; no secrets in VCS.

# 8. Security (Top Priority)
## 8.1 Threat Model (STRIDE-lite)
- Spoofing: Token theft/replay → TLS-only, short access token TTL, httpOnly refresh cookies, rotation & revocation, IP rate limiting.
- Tampering: Payload manipulation → Pydantic schema validation, strict types, server-side checks, signature algorithm pinned.
- Repudiation: Lack of audit → Structured logs (JSON) with correlation IDs; auth events recorded.
- Information Disclosure: Misconfigured CORS/logs → Explicit allowlist; sanitize/redact logs; least-privilege DB users.
- DoS: Brute force/flood → Rate limits on login and public endpoints; timeouts; circuit breakers.
- Elevation of Privilege: JWT forgery/claim abuse → Fixed algorithms (no `none`), issuer/audience validation, downstream `verify` checks, role-based access control roadmap.

## 8.2 Controls & Practices
- Auth
  - Access token TTL: 15–30 min.
  - Refresh token in httpOnly, Secure, SameSite=Lax cookie. Rotate on refresh; revoke on logout.
  - Downstream `authenticate` via `auth-service /verify` only.
- Input Validation
  - Pydantic models with field constraints, explicit length caps, and strict JSON parsing.
- CORS & Headers
  - No wildcard origins; credentials allowed only for trusted domains.
  - Security headers at gateway: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, CSP (basic), HSTS in prod.
- Rate Limiting
  - Login/register and any public endpoints; per-IP and per-identity buckets.
- Logging & Monitoring
  - Redact tokens; include correlation IDs; alert on 4xx/5xx spikes and auth anomalies.
- Secrets & Supply Chain
  - Environment variables/secrets manager only; rotate JWT keys regularly.
  - UV-managed dependencies; `uv.lock` committed; dependency scanning.

# 9. Architecture
## 9.1 Components
- Frontend (Next.js) → API Gateway (8000)
  - → auth-service (8001)
  - → analytics-service (8006)
  - → enterprise_api (verify endpoints)

## 9.2 Flows
- Login: FE → `/api/v1/auth/login` → auth-service returns `{ access_token, user }` → FE stores in session.
- Verify: Downstream services call `auth-service /verify` with incoming Bearer token.
- Analytics: FE → `/api/v1/analytics/metrics` → analytics-service verifies token via auth-service → persists metric.
- Public Verify: FE → `/api/v1/verify*` → forwarded to enterprise_api verify.

# 10. API Specifications (MVP)
## 10.1 Auth (via Gateway)
- `POST /api/v1/auth/register` → `{ success, data: { id, email }, error: null }`
- `POST /api/v1/auth/login` → `{ success, data: { access_token, user: { id, email, roles? } }, error: null }`
- `POST /api/v1/auth/refresh` → `{ success, data: { access_token }, error: null }`
- `POST /api/v1/auth/logout` → `{ success, data: { message }, error: null }`
- `POST /api/v1/auth/verify` → `{ success, data: { id, email, roles? }, error: null }`

## 10.2 Analytics (via Gateway)
- `POST /api/v1/analytics/metrics` → `{ success, data: Metric, error: null }`
- `GET /api/v1/analytics/usage?days=30` → `{ success, data: UsageStats, error: null }`

## 10.3 Public Verify (via Gateway)
- `GET /api/v1/verify*` → forwarded; response shape preserved.

# 11. Configuration & Environments
## 11.1 Gateway ENV
- `GATEWAY_PORT=8000`
- `ALLOWED_ORIGINS=https://encypherai.com,https://www.encypherai.com,http://localhost:3000`
- `AUTH_SERVICE_URL=http://auth-service:8001`
- `ANALYTICS_SERVICE_URL=http://analytics-service:8006`
- `ENTERPRISE_API_URL=http://enterprise-api:9000` (or actual)
- `LOG_LEVEL=INFO`

## 11.2 auth-service
- `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `ALLOWED_ORIGINS`, `LOG_LEVEL`

## 11.3 analytics-service
- `DATABASE_URL`, `REDIS_URL`, `AUTH_SERVICE_URL`, `ALLOWED_ORIGINS`, `LOG_LEVEL`

## 11.4 Frontend
- `NEXT_PUBLIC_API_BASE_URL` → gateway origin

# 12. Migration & Rollout
## 12.1 Phases
1) Gateway Skeleton
   - Implement gateway; proxy all routes to legacy if necessary; CORS/health/metrics/logging.
2) Auth Cutover
   - Route `/api/v1/auth/*` to auth-service; NextAuth uses gateway login.
   - Validate refresh rotation and logout flows.
3) Analytics Integration
   - Route `/api/v1/analytics/*` to analytics-service; send events from FE.
4) Public Verify
   - Route `/api/v1/verify*` to enterprise_api.
5) Cleanup
   - Remove legacy backend usage/config.

## 12.2 Rollback
- Keep legacy backend behind a feature flag/proxy path to restore previous API quickly.
- Toggle gateway route map to revert individual domains (auth/analytics/verify) as needed.

# 13. Acceptance Criteria
- Frontend authenticates via gateway and receives access token; protected pages work.
- Analytics events from FE are accepted, authenticated, and visible in queries.
- Verification endpoints work via gateway using existing frontend paths.
- CORS/headers validated and consistent with security policy.
- Health and metrics endpoints are live; logs contain correlation IDs.

# 14. Risks & Mitigations
- Token/claim mismatches break NextAuth → Align response shape; contract tests; e2e sign-in test.
- Anonymous analytics misuse → Rate limits, captcha (if abused), blocklists, minimal payload.
- CORS misconfiguration → Deploy per-env configs; automated smoke tests.
- Operational complexity → Compose profiles for local dev; docs and runbooks; alerts on failures.

# 15. Dependencies
- auth-service, analytics-service, enterprise_api
- Docker, UV, Postgres, Redis

# 16. Testing Strategy
- Unit tests: gateway routing, auth responses, analytics validation.
- Integration: FE → gateway → services happy paths and error paths.
- Security tests: rate limits, invalid tokens, CORS, header policies.
- Load tests: p95/p99 latency, throughput.

# 17. Documentation Updates
- Update component READMEs: gateway, auth-service, analytics-service configuration examples.
- Update root documentation indices to include this PRD.
- Update `.env.example` files for new variables.

# 18. Work Breakdown Structure (WBS)
- 1.0 API Gateway
  - 1.1 Scaffold service structure (UV, FastAPI, CORS, health, metrics, logging)
  - 1.2 Route mapping for auth/analytics/verify
  - 1.3 Security headers & correlation IDs
- 2.0 Auth Integration
  - 2.1 Register/login/refresh/logout/verify endpoints verified end-to-end
  - 2.2 NextAuth credentials provider integration
  - 2.3 Rate limiting & error handling
- 3.0 Analytics Integration
  - 3.1 Authenticated metrics ingestion from FE
  - 3.2 Usage queries exposed and validated
  - 3.3 Optional anonymous pageview endpoint + safeguards
- 4.0 Verify Routing
  - 4.1 Proxy `/api/v1/verify*` to enterprise_api
  - 4.2 Health checks and smoke tests
- 5.0 Cleanup & Docs
  - 5.1 Remove legacy backend dependencies
  - 5.2 Update READMEs and .env.example files

# 19. Timeline & Milestones (Indicative)
- Week 1: Gateway skeleton, Auth cutover
- Week 2: Analytics instrumentation and dashboards
- Week 3: Verify routing and cleanup; production hardening

# 20. Open Questions
- Do we require anonymous analytics? If yes, define minimal schema and abuse safeguards.
  - A: Ideally we have some analytics, we currently use Google Analytics and Zoho SalesIQ. 
- Do we need social login (Google/GitHub) in MVP, or email/password only?
  - A: Keep google/github for MVP in addition to email/password.
- What production rate limits are acceptable per endpoint and per IP?
  - A: follow industry best practices.

# 21. Appendix: Standard Response Format
```
{
  "success": boolean,
  "data": object | array | null,
  "error": {
    "code": string,
    "message": string,
    "details": object | null
  } | null
}
```
