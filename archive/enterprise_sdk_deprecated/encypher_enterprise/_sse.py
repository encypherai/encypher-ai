"""
Helpers for parsing server-sent events (SSE) returned by the Enterprise API.
"""
from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, Iterable, Iterator, List, Optional

from .models import StreamEvent


def _build_event(event_name: Optional[str], data_lines: List[str]) -> Optional[StreamEvent]:
    if not data_lines and not event_name:
        return None

    data_payload = "\n".join(data_lines).strip()
    parsed_data: Any
    if data_payload:
        try:
            parsed_data = json.loads(data_payload)
        except json.JSONDecodeError:
            parsed_data = data_payload
    else:
        parsed_data = {}

    raw: Dict[str, Any] = {"data": data_payload}
    if event_name:
        raw["event"] = event_name

    return StreamEvent(
        event=event_name or "message",
        data=parsed_data,
        raw=raw,
    )


def iter_sse_events(lines: Iterable[str]) -> Iterator[StreamEvent]:
    """
    Parse a synchronous iterator of SSE lines into StreamEvent objects.
    """
    event_name: Optional[str] = None
    data_lines: List[str] = []

    for raw_line in lines:
        if raw_line is None:
            continue
        line = raw_line.strip("\r")
        if not line:
            event = _build_event(event_name, data_lines)
            if event:
                yield event
            event_name = None
            data_lines = []
            continue

        if line.startswith(":"):
            # Comment/heartbeat
            continue
        if line.startswith("event:"):
            event_name = line[len("event:") :].strip()
            continue
        if line.startswith("data:"):
            data_lines.append(line[len("data:") :].strip())
            continue

        # Fallback: treat as data line
        data_lines.append(line)

    # Flush remainder
    event = _build_event(event_name, data_lines)
    if event:
        yield event


async def aiter_sse_events(lines: AsyncIterator[str]) -> AsyncIterator[StreamEvent]:
    """
    Parse an asynchronous iterator of SSE lines.
    """
    event_name: Optional[str] = None
    data_lines: List[str] = []

    async for raw_line in lines:
        if raw_line is None:
            continue
        line = raw_line.strip("\r")
        if not line:
            event = _build_event(event_name, data_lines)
            if event:
                yield event
            event_name = None
            data_lines = []
            continue

        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event_name = line[len("event:") :].strip()
            continue
        if line.startswith("data:"):
            data_lines.append(line[len("data:") :].strip())
            continue

        data_lines.append(line)

    event = _build_event(event_name, data_lines)
    if event:
        yield event
