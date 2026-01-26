# Enterprise API Disaster Recovery Runbook

**Status**: Drafted for production readiness review
**Scope**: Database restore and failover procedures
**Owners**: SRE + Platform

## 1. Recovery Targets
- **RTO**: 4 hours
- **RPO**: 15 minutes

## 2. Preconditions
- Automated backups enabled.
- Replica instances ready for promotion.
- DNS failover mechanisms configured.

## 3. Recovery Steps
1. Declare incident and freeze writes.
2. Promote replica to primary (or restore from backup).
3. Update connection strings / DNS to new primary.
4. Run `uv run pytest enterprise_api/tests/integration/test_health.py` (or health check) to validate service.
5. Monitor error rates and latency.

## 4. Restore Drill
- Quarterly restore drills required.
- Capture timestamps and evidence for compliance.

## 5. References
- `enterprise_api/docs/DEPLOYMENT.md`
