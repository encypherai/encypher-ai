"""Minimal in-memory metrics collectors for the Enterprise API.

DEPRECATED (TEAM_218): This in-process Counter is a dead-end.
- Resets on every deploy
- Does not aggregate across replicas
- Nothing scrapes /metrics in production (no Prometheus)

Use MetricsService.emit() (app/services/metrics_service.py) which routes events
through Redis Streams -> analytics-service -> PostgreSQL.

TODO(TEAM_218): Remove this module once streaming.py migrates away from increment().
"""

from collections import Counter

_counters: Counter[str] = Counter()


def increment(name: str, value: int = 1) -> None:
    _counters[name] += value


def render_prometheus() -> str:
    lines = []
    for key, value in sorted(_counters.items()):
        lines.append(f"encypher_{key}_total {value}")
    return "\n".join(lines) + "\n"
