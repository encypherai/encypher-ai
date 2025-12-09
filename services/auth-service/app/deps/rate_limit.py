"""
Simple in-memory rate limiting dependency for FastAPI endpoints.
Note: For production, replace with Redis-backed limiter.
"""

import time
from typing import Callable, Dict, Tuple
from fastapi import Request, HTTPException, status
from threading import Lock

# store: {(key, route): [timestamps]}
_store: Dict[Tuple[str, str], list] = {}
_lock = Lock()


def rate_limiter(route: str, limit: int = 10, window_sec: int = 60) -> Callable:
    def _dep(request: Request):
        # prefer X-Forwarded-For if present
        ip = request.headers.get("x-forwarded-for")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        now = time.time()
        key = (ip, route)
        with _lock:
            timestamps = _store.get(key, [])
            # drop older than window
            cutoff = now - window_sec
            timestamps = [t for t in timestamps if t >= cutoff]
            if len(timestamps) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
            timestamps.append(now)
            _store[key] = timestamps

    return _dep
