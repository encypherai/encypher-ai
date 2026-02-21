# Global TODO Tracking

> Incomplete work tracked by AI agents. Each entry includes file, line, and description.

## Format

```markdown
- [ ] `path/to/file.py:123` - TEAM_XXX: Description of what's missing
```

---

## Active TODOs

<!-- Add TODOs below this line -->

### TEAM_218 - Metrics Pipeline + Request Tracing
> See: `.teams/TEAM_218_metrics_pipeline_request_tracing.md`
> PRD: `PRDs/CURRENT/PRD_Metrics_Pipeline_Request_Tracing.md`

- [ ] `services/analytics-service/app/services/` - TEAM_218: Add hourly/daily AggregatedMetric rollup task (asyncio periodic, started in lifespan)
- [ ] `apps/dashboard/` - TEAM_218: Surface RSL analytics per publisher (bot breakdown, fetch trends) on publisher dashboard
- [ ] `enterprise_api/app/observability/metrics.py` - TEAM_218: Full removal of dead-end Counter once all callers migrated to MetricsService

---

## Completed

<!-- Move completed TODOs here with [x] -->
- [x] `.questions/TEAM_068_analytics_routing_decision.md` - TEAM_068: Decided marketing analytics should use analytics-service pageview endpoint and updated routing accordingly.

---

*Last Updated: November 2025*
