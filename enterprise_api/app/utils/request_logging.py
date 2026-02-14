from __future__ import annotations


def _is_health_probe_path(path: str) -> bool:
    return path in {"/health", "/readyz", "/metrics"}


def should_log_request(
    *,
    path: str,
    status_code: int,
    process_time_ms: int,
    request_logging_enabled: bool,
    log_health_checks: bool,
    slow_request_threshold_ms: int,
) -> bool:
    if not log_health_checks and _is_health_probe_path(path):
        return False

    if status_code >= 500:
        return True

    if process_time_ms >= slow_request_threshold_ms:
        return True

    if request_logging_enabled:
        return True

    return False
