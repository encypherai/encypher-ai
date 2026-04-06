# Global TODO Tracking

> Incomplete work tracked by AI agents. Each entry includes file, line, and description.

## Format

```markdown
- [ ] `path/to/file.py:123` - TEAM_XXX: Description of what's missing
```

---

## Active TODOs

<!-- Add TODOs below this line -->

### Spread-Spectrum ECC (Concatenated RS + Convolutional + Soft Viterbi)

Applies to all three signal-domain watermarking surfaces. The concatenated coding scheme (outer RS(32,8) over GF(2^8), inner rate-1/3 K=7 convolutional code, soft-decision Viterbi decoder) is specified in `PRDs/CURRENT/PRD_Video_Soft_Binding.md` section "Error Correction Coding (Concatenated Code)".

- [ ] `services/audio-watermark-service/app/services/spread_spectrum.py` - ECC backport: wrap 64-bit payload in concatenated RS+convolutional code before PN spreading, soft Viterbi decode on detection. Detailed tasks in PRD_Video_Soft_Binding.md section 10.0.
- [ ] `services/video-watermark-service/` (not yet created) - ECC built-in from day one. Detailed tasks in PRD_Video_Soft_Binding.md section 9.0.
- [ ] `services/image-watermark-service/` (not yet created) - Spread-spectrum image watermarking with concatenated ECC, replacing TrustMark dependency (Adobe neural model). Own the algorithm end-to-end. Same PN sequence + ECC architecture as audio/video, applied to spatial-domain pixel luminance. Needs its own PRD.

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
