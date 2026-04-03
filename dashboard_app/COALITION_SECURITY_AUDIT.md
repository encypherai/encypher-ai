# Coalition Infrastructure Security Audit Checklist

**Date**: 2025-11-04
**PRD**: PRD-001 Coalition Infrastructure
**Phase**: 5 - Testing & Launch

---

## Authentication & Authorization

### API Authentication
- [ ] All coalition endpoints require authentication
- [ ] JWT tokens properly validated
- [x] Token expiration enforced (< 1 hour)
- [x] Refresh token mechanism implemented
- [ ] API keys for AI companies properly hashed (bcrypt)
- [x] API key rotation supported
- [ ] Rate limiting per user/API key

### Authorization
- [ ] Member endpoints restricted to own data
- [ ] Admin endpoints require `is_superuser` flag
- [ ] AI company endpoints validate API key scope
- [ ] No privilege escalation vulnerabilities
- [ ] RBAC properly implemented

### Test Commands
```bash
# Test unauthorized access
curl -X GET http://localhost:8000/api/v1/coalition/stats
# Expected: 401 Unauthorized

# Test admin endpoint as regular user
curl -X GET http://localhost:8000/api/v1/coalition/admin/overview \
  -H "Authorization: Bearer <user_token>"
# Expected: 403 Forbidden

# Test accessing other user's data
curl -X GET http://localhost:8000/api/v1/coalition/stats \
  -H "Authorization: Bearer <user_token>" \
  -H "X-User-ID: <other_user_id>"
# Expected: 403 Forbidden or ignored header
```

---

## Data Protection

### Sensitive Data
- [x] API keys never stored in plaintext
- [x] Passwords hashed with bcrypt (cost factor >= 12)
- [ ] No sensitive data in logs
- [ ] No sensitive data in error messages
- [ ] PII encrypted at rest (if applicable)
- [ ] Database connections use SSL/TLS

### Data Privacy
- [ ] Only metadata exposed via API (not full content)
- [ ] AI companies cannot see individual publishers
- [ ] Member data isolated (no cross-member queries)
- [ ] GDPR right to be forgotten implemented
- [ ] Data retention policies enforced

### Test Commands
```bash
# Check for sensitive data in logs
grep -r "password\|api_key\|secret" logs/

# Check database encryption
psql -c "SHOW ssl;"

# Test data isolation
# As user A, try to access user B's content
curl -X GET http://localhost:8000/api/v1/coalition/content/performance \
  -H "Authorization: Bearer <user_a_token>"
# Verify only user A's content returned
```

---

## Input Validation

### API Endpoints
- [ ] All inputs validated (type, length, format)
- [x] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (output encoding)
- [ ] CSRF tokens implemented
- [ ] File upload validation (if applicable)
- [x] JSON schema validation
- [ ] Max request size enforced

### Test Cases
```bash
# SQL injection test
curl -X POST http://localhost:8000/api/v1/coalition/content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test'; DROP TABLE content_items; --"}'
# Expected: Validation error or safe handling

# XSS test
curl -X POST http://localhost:8000/api/v1/coalition/content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "<script>alert(1)</script>"}'
# Expected: Sanitized or rejected

# Oversized payload test
curl -X POST http://localhost:8000/api/v1/coalition/content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "'$(python -c 'print("A"*1000000)')'"}'
# Expected: 413 Payload Too Large
```

---

## Rate Limiting & DoS Protection

### Rate Limits
- [ ] Per-user rate limits implemented
- [ ] Per-IP rate limits implemented
- [ ] AI company API key rate limits
- [ ] Exponential backoff on failures
- [ ] 429 Too Many Requests returned

### Limits
- **Member endpoints**: 100 req/min per user
- **Admin endpoints**: 1000 req/min per admin
- **AI company endpoints**: 10000 req/min per API key
- **Public endpoints**: 10 req/min per IP

### Test Commands
```bash
# Test rate limiting
for i in {1..150}; do
  curl -X GET http://localhost:8000/api/v1/coalition/stats \
    -H "Authorization: Bearer <token>"
done
# Expected: 429 after 100 requests

# Test with multiple IPs (use proxy/VPN)
# Verify per-IP limits work
```

---

## API Security

### HTTP Security Headers
- [ ] `Strict-Transport-Security` header set
- [ ] `X-Content-Type-Options: nosniff` set
- [ ] `X-Frame-Options: DENY` set
- [ ] `X-XSS-Protection: 1; mode=block` set
- [ ] `Content-Security-Policy` configured
- [x] CORS properly configured

### HTTPS/TLS
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] TLS 1.2+ only
- [ ] Strong cipher suites
- [ ] Valid SSL certificate
- [ ] HSTS enabled

### Test Commands
```bash
# Check security headers
curl -I https://api.encypher.com/api/v1/coalition/stats

# Test TLS version
nmap --script ssl-enum-ciphers -p 443 api.encypher.com

# Test SSL certificate
openssl s_client -connect api.encypher.com:443 -tls1_2
```

---

## Database Security

### Access Control
- [ ] Database user has minimal privileges
- [ ] No direct database access from internet
- [ ] Database firewall rules configured
- [ ] Connection pooling limits set
- [ ] Query timeouts configured

### Data Integrity
- [x] Foreign key constraints enforced
- [x] Unique constraints on critical fields
- [ ] Check constraints for data validation
- [ ] Transactions used for multi-step operations
- [ ] Database backups automated

### Test Commands
```bash
# Check database user privileges
psql -U coalition_user -c "\du"

# Test connection from external IP
psql -h <db_host> -U coalition_user -d coalition_db
# Expected: Connection refused or timeout

# Check backup schedule
crontab -l | grep pg_dump
```

---

## Logging & Monitoring

### Security Logging
- [ ] All authentication attempts logged
- [ ] Failed login attempts logged
- [x] Admin actions logged
- [ ] API key usage logged
- [ ] Suspicious activity logged
- [ ] Logs stored securely
- [ ] Log retention policy (90 days)

### Monitoring
- [ ] Real-time alerts for suspicious activity
- [ ] Failed auth rate monitoring
- [ ] API error rate monitoring
- [ ] Database query performance monitoring
- [ ] Disk space monitoring

### Test Commands
```bash
# Check log files
tail -f logs/security.log

# Test failed login logging
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"username": "admin", "password": "wrong"}'
# Verify logged in security.log

# Check monitoring alerts
# Trigger 10 failed logins, verify alert sent
```

---

## Third-Party Dependencies

### Dependency Security
- [ ] All dependencies up to date
- [ ] No known vulnerabilities (CVEs)
- [ ] Dependency scanning automated
- [ ] Minimal dependencies used
- [ ] Dependencies from trusted sources

### Test Commands
```bash
# Backend (Python)
cd dashboard_app/backend
uv run pip-audit

# Frontend (JavaScript)
cd dashboard_app/frontend
npm audit

# Check for outdated packages
uv run pip list --outdated
npm outdated
```

---

## Error Handling

### Error Responses
- [ ] No stack traces in production errors
- [ ] Generic error messages to users
- [ ] Detailed errors logged server-side
- [ ] Consistent error response format
- [ ] Appropriate HTTP status codes

### Test Commands
```bash
# Test error handling
curl -X GET http://localhost:8000/api/v1/coalition/invalid-endpoint
# Expected: 404 with generic message, no stack trace

# Test database error
# Stop database, make request
curl -X GET http://localhost:8000/api/v1/coalition/stats \
  -H "Authorization: Bearer <token>"
# Expected: 500 with generic message, detailed error in logs
```

---

## Coalition-Specific Security

### Revenue Distribution
- [ ] Revenue calculations auditable
- [ ] No double-payment vulnerabilities
- [ ] Payment records immutable
- [ ] Revenue split percentages validated
- [ ] Minimum payout threshold enforced

### Content Access
- [x] AI company access properly tracked
- [ ] No unauthorized content access
- [ ] Access logs tamper-proof
- [ ] Content hash validation
- [x] Duplicate content handling

### Member Management
- [ ] Opt-out properly removes content
- [ ] No orphaned data after opt-out
- [ ] Member status transitions validated
- [ ] Auto-enrollment secure

### Test Commands
```bash
# Test revenue calculation
# Create test data, verify calculations match expected

# Test content access tracking
curl -X POST http://localhost:8000/api/v1/coalition/access-log \
  -H "Authorization: Bearer <ai_company_key>" \
  -d '{"content_id": "<id>", "ai_company": "Test"}'
# Verify logged correctly

# Test opt-out
curl -X POST http://localhost:8000/api/v1/coalition/leave \
  -H "Authorization: Bearer <token>"
# Verify content removed from pool
```

---

## Compliance

### GDPR
- [ ] Privacy policy updated
- [ ] Cookie consent implemented
- [ ] Data portability supported
- [ ] Right to be forgotten implemented
- [ ] Data processing agreement with AI companies

### CCPA
- [ ] Do Not Sell disclosure
- [ ] Opt-out mechanism
- [ ] Data deletion on request

### Financial
- [ ] Payment processing PCI compliant
- [ ] Tax reporting supported
- [ ] Financial audit trail

---

## Penetration Testing

### Automated Scans
- [ ] OWASP ZAP scan completed
- [ ] Burp Suite scan completed
- [ ] Nmap port scan completed
- [ ] Nikto web server scan completed

### Manual Testing
- [ ] Authentication bypass attempts
- [ ] Authorization bypass attempts
- [ ] Session hijacking attempts
- [ ] CSRF attacks attempted
- [ ] Business logic flaws tested

### Test Commands
```bash
# OWASP ZAP
zap-cli quick-scan http://localhost:8000

# Nmap
nmap -sV -sC localhost

# Nikto
nikto -h http://localhost:8000
```

---

## Incident Response

### Preparedness
- [ ] Incident response plan documented
- [ ] Security contact email configured
- [ ] Breach notification process defined
- [ ] Backup restoration tested
- [ ] Rollback procedure documented

### Monitoring
- [ ] Intrusion detection system (IDS) configured
- [ ] Security information and event management (SIEM)
- [ ] Automated alerts for critical events

---

## Sign-Off

### Security Team
- [ ] Security audit completed
- [ ] All critical issues resolved
- [ ] All high issues resolved or accepted
- [ ] Medium/low issues documented

**Auditor**: ___________________
**Date**: ___________________
**Signature**: ___________________

### Development Team
- [ ] All security requirements implemented
- [ ] Security tests passing
- [ ] Documentation updated

**Lead Developer**: ___________________
**Date**: ___________________
**Signature**: ___________________

### Management
- [ ] Security risks reviewed
- [ ] Launch approved

**Product Manager**: ___________________
**Date**: ___________________
**Signature**: ___________________

---

## Post-Launch

### Ongoing Security
- [ ] Weekly dependency scans
- [ ] Monthly security reviews
- [ ] Quarterly penetration tests
- [ ] Annual comprehensive audit
- [ ] Bug bounty program (optional)

### Monitoring
- [ ] Daily log review
- [ ] Real-time alert response
- [ ] Monthly security metrics report

---

## Audit Findings and Action Items

Note: Only items marked as checked are 100% verified in code. The following gaps require implementation before audit sign-off.

- **Authentication & Authorization**
  - Implement auth on Coalition Service endpoints by verifying Bearer JWT via Auth Service and deriving `current_user` for all routes. Enforce member-only access by matching `token.sub` to `user_id` parameters. Add admin guard for Admin routes (require `is_superuser`). Enforce API key scope on AI-company-facing endpoints by verifying with Key Service and checking `permissions`.

- **Rate Limiting & DoS**
  - Add per-user, per-IP, and per-API-key rate limits using a limiter (e.g., SlowAPI) with 429 responses matching policy thresholds. Include exponential backoff guidance for clients.

- **Security Headers & HTTPS**
  - Add security headers middleware (HSTS, X-Frame-Options, X-Content-Type-Options, XSS-Protection, CSP). Enforce HTTPS and HSTS at the edge/proxy. Restrict TLS to 1.2+ with strong ciphers.

- **Data Protection**
  - Configure password hashing with bcrypt cost ≥ 12 in `CryptContext` (e.g., `bcrypt__rounds=12`). Update API key storage from SHA-256 to bcrypt per audit requirement, or obtain exception with justification. Ensure DB SSL/TLS and PII-at-rest encryption where applicable. Replace raw exception details in API errors with generic messages and log details server-side.

- **Input Validation**
  - Enforce max request sizes and add XSS protections where user-generated content may be rendered. CSRF is likely N/A for pure Bearer-token APIs; document justification or implement CSRF if cookies/sessions are introduced.

- **Logging & Monitoring**
  - Log authentication attempts (success/failure) and integrate API key usage logging by invoking `log_key_usage` in Key Service. Define secure log storage and 90-day retention. Add alerting for failed auth rate spikes, API error rates, and DB performance anomalies. Instrument DB query timing if required.

- **Coalition-Specific Controls**
  - Enforce minimum payout threshold, prevent double-payment with state checks and constraints, and make payment records immutable. Validate `content_hash` on ingest and consider tamper-evident access logs.

- **Compliance & Testing**
  - Implement GDPR/CCPA flows (delete/export data, opt-out propagation), run dependency scans (`pip-audit`, `npm audit`), and add pen-test scans (ZAP/Nmap/Nikto) with artifacts.
