"""Tests for incident fingerprinting, deduplication, and lifecycle."""

import pytest

from app.services.incident_service import (
    classify_severity,
    compute_fingerprint,
    normalize_endpoint,
)


class TestNormalizeEndpoint:
    def test_uuid_in_path(self):
        assert normalize_endpoint("/api/v1/keys/550e8400-e29b-41d4-a716-446655440000") == "/api/v1/keys/{uuid}"

    def test_hex_id_in_path(self):
        assert normalize_endpoint("/api/v1/documents/abc123def456789012345678") == "/api/v1/documents/{id}"  # pragma: allowlist secret

    def test_numeric_id_in_path(self):
        assert normalize_endpoint("/api/v1/users/12345") == "/api/v1/users/{n}"

    def test_no_params(self):
        assert normalize_endpoint("/api/v1/sign") == "/api/v1/sign"

    def test_empty_string(self):
        assert normalize_endpoint("") == ""

    def test_multiple_params(self):
        result = normalize_endpoint("/api/v1/org/12345/members/67890")
        assert result == "/api/v1/org/{n}/members/{n}"


class TestComputeFingerprint:
    def test_same_inputs_same_fingerprint(self):
        fp1 = compute_fingerprint("auth-service", "/api/v1/auth/login", "E_UNAUTHORIZED", 401)
        fp2 = compute_fingerprint("auth-service", "/api/v1/auth/login", "E_UNAUTHORIZED", 401)
        assert fp1 == fp2

    def test_different_service_different_fingerprint(self):
        fp1 = compute_fingerprint("auth-service", "/api/v1/auth/login", "E_UNAUTHORIZED", 401)
        fp2 = compute_fingerprint("key-service", "/api/v1/auth/login", "E_UNAUTHORIZED", 401)
        assert fp1 != fp2

    def test_path_params_normalized(self):
        fp1 = compute_fingerprint("enterprise-api", "/api/v1/keys/abc123def456789012345678", "E_NOT_FOUND", 404)
        fp2 = compute_fingerprint("enterprise-api", "/api/v1/keys/def456abc789012345678901", "E_NOT_FOUND", 404)
        assert fp1 == fp2

    def test_returns_32_char_hex(self):
        fp = compute_fingerprint("svc", "/path", "ERR", 500)
        assert len(fp) == 32
        assert all(c in "0123456789abcdef" for c in fp)


class TestClassifySeverity:
    def test_critical_error_code(self):
        assert classify_severity("E_INTERNAL") == "critical"
        assert classify_severity("E_UNHANDLED") == "critical"
        assert classify_severity("E_SERVICE_UNAVAILABLE") == "critical"

    def test_critical_status_code(self):
        assert classify_severity("UNKNOWN", 500) == "critical"
        assert classify_severity("UNKNOWN", 502) == "critical"

    def test_warning_rate_limit(self):
        assert classify_severity("E_RATE_LIMIT") == "warning"
        assert classify_severity("E_QUOTA_EXCEEDED") == "warning"

    def test_warning_4xx(self):
        assert classify_severity("E_NOT_FOUND", 404) == "warning"

    def test_info_default(self):
        assert classify_severity("SOMETHING") == "info"
