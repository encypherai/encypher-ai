"""Tests for endpoint error suppression in the alert pipeline."""

import pytest
from unittest.mock import patch

from app.core.config import Settings
from app.services.stream_consumer import AlertStreamConsumer


class TestParsedSuppressionRules:
    """Config parsing for SUPPRESSED_ENDPOINT_PATTERNS."""

    def test_empty_string(self):
        s = Settings(SUPPRESSED_ENDPOINT_PATTERNS="")
        assert s.parsed_suppression_rules == []

    def test_whitespace_only(self):
        s = Settings(SUPPRESSED_ENDPOINT_PATTERNS="   ")
        assert s.parsed_suppression_rules == []

    def test_single_rule(self):
        s = Settings(SUPPRESSED_ENDPOINT_PATTERNS="404:/api/v1/integrations/ghost")
        assert s.parsed_suppression_rules == [(404, "/api/v1/integrations/ghost")]

    def test_multiple_rules(self):
        s = Settings(SUPPRESSED_ENDPOINT_PATTERNS="404:/api/v1/integrations/ghost,404:/api/v1/cdn/cloudflare,403:/api/v1/enterprise/c2pa/templates")
        rules = s.parsed_suppression_rules
        assert len(rules) == 3
        assert (404, "/api/v1/integrations/ghost") in rules
        assert (404, "/api/v1/cdn/cloudflare") in rules
        assert (403, "/api/v1/enterprise/c2pa/templates") in rules

    def test_whitespace_trimmed(self):
        s = Settings(SUPPRESSED_ENDPOINT_PATTERNS="  404 : /api/ghost , 500:/api/error  ")
        rules = s.parsed_suppression_rules
        assert rules == [(404, "/api/ghost"), (500, "/api/error")]

    def test_malformed_entries_skipped(self):
        s = Settings(SUPPRESSED_ENDPOINT_PATTERNS="404:/valid,no-colon,abc:/invalid-code,200:/ok")
        rules = s.parsed_suppression_rules
        assert rules == [(404, "/valid"), (200, "/ok")]


class TestIsSuppressed:
    """AlertStreamConsumer._is_suppressed static method."""

    def test_matching_rule(self):
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            assert AlertStreamConsumer._is_suppressed(404, "/api/v1/integrations/ghost") is True

    def test_prefix_match(self):
        rules = [(404, "/api/v1/integrations/")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            assert AlertStreamConsumer._is_suppressed(404, "/api/v1/integrations/ghost") is True
            assert AlertStreamConsumer._is_suppressed(404, "/api/v1/integrations/wordpress/status") is True

    def test_status_code_mismatch(self):
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            assert AlertStreamConsumer._is_suppressed(500, "/api/v1/integrations/ghost") is False

    def test_endpoint_mismatch(self):
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            assert AlertStreamConsumer._is_suppressed(404, "/api/v1/keys") is False

    def test_no_rules(self):
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = []
            assert AlertStreamConsumer._is_suppressed(404, "/api/v1/anything") is False


class TestIsErrorEventSuppression:
    """Integration test: _is_error_event respects suppression rules."""

    def setup_method(self):
        self.consumer = AlertStreamConsumer.__new__(AlertStreamConsumer)

    def test_suppressed_404_returns_false(self):
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            data = {"status_code": "404", "endpoint": "/api/v1/integrations/ghost"}
            assert self.consumer._is_error_event(data) is False

    def test_non_suppressed_404_returns_true(self):
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            data = {"status_code": "404", "endpoint": "/api/v1/keys/abc123"}
            assert self.consumer._is_error_event(data) is True

    def test_500_never_suppressed_by_404_rule(self):
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            data = {"status_code": "500", "endpoint": "/api/v1/integrations/ghost"}
            assert self.consumer._is_error_event(data) is True

    def test_error_code_events_bypass_suppression(self):
        """Events with explicit error_code/error_message are never suppressed."""
        rules = [(404, "/api/v1/integrations/ghost")]
        with patch("app.services.stream_consumer.settings") as mock_settings:
            mock_settings.parsed_suppression_rules = rules
            data = {"error_code": "E_UNHANDLED", "error_message": "something broke"}
            assert self.consumer._is_error_event(data) is True
