from app.utils.request_logging import should_log_request


def test_should_not_log_health_probe_by_default() -> None:
    assert not should_log_request(
        path="/health",
        status_code=200,
        process_time_ms=12,
        request_logging_enabled=False,
        log_health_checks=False,
        slow_request_threshold_ms=2000,
    )


def test_should_log_server_errors_even_when_request_logging_disabled() -> None:
    assert should_log_request(
        path="/api/v1/sign",
        status_code=500,
        process_time_ms=45,
        request_logging_enabled=False,
        log_health_checks=False,
        slow_request_threshold_ms=2000,
    )


def test_should_log_slow_request_even_when_success() -> None:
    assert should_log_request(
        path="/api/v1/sign",
        status_code=200,
        process_time_ms=2500,
        request_logging_enabled=False,
        log_health_checks=False,
        slow_request_threshold_ms=2000,
    )


def test_should_log_success_request_when_explicitly_enabled() -> None:
    assert should_log_request(
        path="/api/v1/sign",
        status_code=200,
        process_time_ms=30,
        request_logging_enabled=True,
        log_health_checks=False,
        slow_request_threshold_ms=2000,
    )
