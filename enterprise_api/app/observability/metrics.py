"""Minimal in-memory metrics collectors for the Enterprise API."""
from collections import Counter
from typing import Dict

_counters: Counter[str] = Counter()


def increment(name: str, value: int = 1) -> None:
    _counters[name] += value


def render_prometheus() -> str:
    lines = []
    for key, value in sorted(_counters.items()):
        lines.append(f"encypher_{key}_total {value}")
    return "\n".join(lines) + "\n"
