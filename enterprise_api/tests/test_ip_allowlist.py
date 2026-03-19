"""Tests for API key IP allowlist feature."""

import pytest

from app.dependencies import check_ip_allowlist


class TestCheckIpAllowlist:
    """Unit tests for check_ip_allowlist."""

    def test_empty_allowlist_allows_all(self):
        assert check_ip_allowlist([], "1.2.3.4") is True
        assert check_ip_allowlist([], "::1") is True

    def test_ipv4_cidr_match(self):
        assert check_ip_allowlist(["10.0.0.0/8"], "10.1.2.3") is True
        assert check_ip_allowlist(["10.0.0.0/8"], "10.255.255.255") is True

    def test_ipv4_cidr_no_match(self):
        assert check_ip_allowlist(["10.0.0.0/8"], "192.168.1.1") is False

    def test_ipv4_single_host(self):
        assert check_ip_allowlist(["192.168.1.1/32"], "192.168.1.1") is True
        assert check_ip_allowlist(["192.168.1.1/32"], "192.168.1.2") is False

    def test_ipv6_cidr_match(self):
        assert check_ip_allowlist(["2001:db8::/32"], "2001:db8::1") is True
        assert check_ip_allowlist(["2001:db8::/32"], "2001:db8:ffff::1") is True

    def test_ipv6_cidr_no_match(self):
        assert check_ip_allowlist(["2001:db8::/32"], "2001:db9::1") is False

    def test_multiple_cidrs(self):
        allowlist = ["10.0.0.0/8", "192.168.0.0/16"]
        assert check_ip_allowlist(allowlist, "10.1.2.3") is True
        assert check_ip_allowlist(allowlist, "192.168.1.1") is True
        assert check_ip_allowlist(allowlist, "172.16.0.1") is False

    def test_mixed_ipv4_ipv6(self):
        allowlist = ["10.0.0.0/8", "2001:db8::/32"]
        assert check_ip_allowlist(allowlist, "10.0.0.1") is True
        assert check_ip_allowlist(allowlist, "2001:db8::1") is True
        assert check_ip_allowlist(allowlist, "172.16.0.1") is False

    def test_invalid_client_ip_returns_false(self):
        assert check_ip_allowlist(["10.0.0.0/8"], "not-an-ip") is False
        assert check_ip_allowlist(["10.0.0.0/8"], "") is False

    def test_invalid_cidr_entry_is_skipped(self):
        # Invalid CIDR entries are skipped; valid ones still match
        assert check_ip_allowlist(["bad-cidr", "10.0.0.0/8"], "10.1.2.3") is True

    def test_all_invalid_cidrs_returns_false(self):
        # If all entries are invalid, nothing matches
        assert check_ip_allowlist(["bad1", "bad2"], "10.0.0.1") is False

    def test_strict_false_allows_host_bits(self):
        # strict=False means "192.168.1.100/24" is treated as "192.168.1.0/24"
        assert check_ip_allowlist(["192.168.1.100/24"], "192.168.1.50") is True
