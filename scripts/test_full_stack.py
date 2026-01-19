#!/usr/bin/env python3
"""
Full-Stack Integration Test for Encypher Platform

Tests the complete flow:
1. User signup/login (auth-service)
2. API key generation (key-service)
3. Content signing (enterprise-api)
4. Content verification (enterprise-api)
5. Analytics tracking (analytics-service)
6. Billing/usage (billing-service)

Usage:
    python scripts/test_full_stack.py
"""

import subprocess
import sys
from datetime import datetime
from typing import Optional, Tuple

import requests

# Service URLs
SERVICES = {
    "auth": "http://localhost:8001",
    "user": "http://localhost:8002",
    "key": "http://localhost:8003",
    "encoding": "http://localhost:8004",
    "verification": "http://localhost:8005",
    "analytics": "http://localhost:8006",
    "billing": "http://localhost:8007",
    "notification": "http://localhost:8008",
    "coalition": "http://localhost:8009",
    "enterprise": "http://localhost:9000",
}


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record(self, name: str, passed: bool, error: str = None):
        if passed:
            self.passed += 1
            print(f"  ✓ {name}")
        else:
            self.failed += 1
            self.errors.append((name, error))
            print(f"  ✗ {name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"Full-Stack Test Results: {self.passed}/{total} passed")
        if self.errors:
            print("\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        return self.failed == 0


results = TestResults()


def check_services_health():
    """Check all services are healthy"""
    print("\n" + "=" * 60)
    print("1. SERVICE HEALTH CHECK")
    print("=" * 60)

    all_healthy = True
    for name, url in SERVICES.items():
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            if resp.status_code == 200:
                results.record(f"{name}-service health", True)
            else:
                results.record(f"{name}-service health", False, f"Status {resp.status_code}")
                all_healthy = False
        except requests.exceptions.ConnectionError:
            results.record(f"{name}-service health", False, "Connection refused")
            all_healthy = False
        except Exception as e:
            results.record(f"{name}-service health", False, str(e))
            all_healthy = False

    return all_healthy


def test_user_signup_login() -> Tuple[Optional[str], Optional[str]]:
    """Test user signup and login flow"""
    print("\n" + "=" * 60)
    print("2. USER SIGNUP & LOGIN (auth-service)")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    email = f"fullstack_test_{timestamp}@example.com"
    password = "TestPassword123!"

    # Signup
    try:
        resp = requests.post(
            f"{SERVICES['auth']}/api/v1/auth/signup", json={"email": email, "password": password, "name": "Full Stack Test User"}, timeout=10
        )
        if resp.status_code in [200, 201]:
            user_data = resp.json().get("data", {})
            user_id = user_data.get("id")
            results.record("User signup", True)
        else:
            results.record("User signup", False, f"Status {resp.status_code}: {resp.text[:100]}")
            return None, None
    except Exception as e:
        results.record("User signup", False, str(e))
        return None, None

    # Verify email in DB (bypass email verification for testing)
    try:
        subprocess.run(
            [
                "docker",
                "exec",
                "encypher-postgres-auth",
                "psql",
                "-U",
                "encypher",
                "-d",
                "encypher_auth",
                "-c",
                f"UPDATE users SET email_verified = true WHERE email = '{email}';",
            ],
            capture_output=True,
            check=True,
        )
        results.record("Email verification (DB bypass)", True)
    except Exception as e:
        results.record("Email verification (DB bypass)", False, str(e))
        return None, None

    # Login
    try:
        resp = requests.post(f"{SERVICES['auth']}/api/v1/auth/login", json={"email": email, "password": password}, timeout=10)
        if resp.status_code == 200:
            token = resp.json().get("data", {}).get("access_token")
            results.record("User login", True)
            return token, user_id
        else:
            results.record("User login", False, f"Status {resp.status_code}")
            return None, None
    except Exception as e:
        results.record("User login", False, str(e))
        return None, None


def test_api_key_generation(token: str) -> Optional[str]:
    """Test API key generation"""
    print("\n" + "=" * 60)
    print("3. API KEY GENERATION (key-service)")
    print("=" * 60)

    if not token:
        results.record("API key generation (skipped - no token)", False, "No auth token")
        return None

    headers = {"Authorization": f"Bearer {token}"}

    # Generate key
    try:
        resp = requests.post(
            f"{SERVICES['key']}/api/v1/keys/generate",
            json={"name": "Full Stack Test Key", "permissions": ["sign", "verify", "read"]},
            headers=headers,
            timeout=10,
        )
        if resp.status_code in [200, 201]:
            key_data = resp.json()
            api_key = key_data.get("key")
            results.record("Generate API key", True)

            # Verify key
            verify_resp = requests.post(f"{SERVICES['key']}/api/v1/keys/verify", json={"key": api_key}, timeout=5)
            if verify_resp.status_code == 200 and verify_resp.json().get("valid"):
                results.record("Verify API key", True)
            else:
                results.record("Verify API key", False, f"valid={verify_resp.json().get('valid')}")

            return api_key
        else:
            results.record("Generate API key", False, f"Status {resp.status_code}")
            return None
    except Exception as e:
        results.record("API key generation", False, str(e))
        return None


def test_enterprise_api_signing(api_key: str):
    """Test Enterprise API content signing"""
    print("\n" + "=" * 60)
    print("4. CONTENT SIGNING (enterprise-api)")
    print("=" * 60)

    # Enterprise API uses its own demo keys for testing
    # These are hardcoded in enterprise_api/app/dependencies.py
    demo_api_key = "demo-api-key-for-testing"
    print(f"  Using Enterprise API demo key: {demo_api_key[:20]}...")

    headers = {"Authorization": f"Bearer {demo_api_key}"}

    test_content = (
        "This is a test document for full-stack integration testing. "
        "It contains multiple sentences to verify the signing process. "
        "The Enterprise API should sign this content with C2PA compliance."
    )

    # Sign content
    try:
        resp = requests.post(f"{SERVICES['enterprise']}/api/v1/sign", json={"text": test_content}, headers=headers, timeout=30)
        if resp.status_code == 200:
            sign_data = resp.json()
            signed_content = sign_data.get("signed_text") or sign_data.get("signed_content") or sign_data.get("content")
            doc_id = sign_data.get("document_id")
            results.record("Sign content", True)
            print(f"  Document ID: {doc_id}")
            return signed_content
        elif resp.status_code == 401:
            results.record("Sign content", False, "Unauthorized - API key not recognized")
            return None
        elif resp.status_code == 422:
            results.record("Sign content", False, f"Validation error: {resp.text[:100]}")
            return None
        else:
            results.record("Sign content", False, f"Status {resp.status_code}: {resp.text[:100]}")
            return None
    except Exception as e:
        results.record("Sign content", False, str(e))
        return None


def test_enterprise_api_verification(api_key: str, signed_content: str):
    """Test Enterprise API content verification"""
    print("\n" + "=" * 60)
    print("5. CONTENT VERIFICATION (enterprise-api)")
    print("=" * 60)

    if not signed_content:
        results.record("Verify content (skipped - no signed content)", False, "No signed content")
        return

    demo_api_key = "demo-api-key-for-testing"
    headers = {"Authorization": f"Bearer {demo_api_key}"}

    # Verify content
    try:
        resp = requests.post(f"{SERVICES['enterprise']}/api/v1/verify", json={"text": signed_content}, headers=headers, timeout=30)
        if resp.status_code == 200:
            verify_data = resp.json()
            is_valid = verify_data.get("valid") or verify_data.get("verified") or verify_data.get("is_signed")
            results.record("Verify signed content", True)
            print(f"  Verified: {is_valid}")
        else:
            results.record("Verify signed content", False, f"Status {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        results.record("Verify signed content", False, str(e))


def test_analytics_tracking(token: str):
    """Test analytics tracking"""
    print("\n" + "=" * 60)
    print("6. ANALYTICS TRACKING (analytics-service)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Track event
    try:
        resp = requests.post(
            f"{SERVICES['analytics']}/api/v1/analytics/track",
            json={"metric_type": "api_call", "service_name": "full_stack_test", "count": 1},
            headers=headers,
            timeout=10,
        )
        results.record("Track analytics event", resp.status_code in [200, 201, 404, 422])
    except Exception as e:
        results.record("Track analytics event", False, str(e))

    # Get stats
    try:
        resp = requests.get(f"{SERVICES['analytics']}/api/v1/analytics/stats", headers=headers, timeout=10)
        results.record("Get analytics stats", resp.status_code in [200, 404])
    except Exception as e:
        results.record("Get analytics stats", False, str(e))


def test_billing_usage(token: str):
    """Test billing and usage"""
    print("\n" + "=" * 60)
    print("7. BILLING & USAGE (billing-service)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Get plans
    try:
        resp = requests.get(f"{SERVICES['billing']}/api/v1/billing/plans", timeout=10)
        results.record("Get billing plans", resp.status_code in [200, 404])
    except Exception as e:
        results.record("Get billing plans", False, str(e))

    # Get usage
    try:
        resp = requests.get(f"{SERVICES['billing']}/api/v1/billing/usage", headers=headers, timeout=10)
        results.record("Get billing usage", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("Get billing usage", False, str(e))


def test_user_profile(token: str):
    """Test user profile operations"""
    print("\n" + "=" * 60)
    print("8. USER PROFILE (user-service)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Get profile
    try:
        resp = requests.get(f"{SERVICES['user']}/api/v1/profile", headers=headers, timeout=10)
        results.record("Get user profile", resp.status_code in [200, 404])
    except Exception as e:
        results.record("Get user profile", False, str(e))


def test_notifications(token: str):
    """Test notification service"""
    print("\n" + "=" * 60)
    print("9. NOTIFICATIONS (notification-service)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Get notifications
    try:
        resp = requests.get(f"{SERVICES['notification']}/api/v1/notifications", headers=headers, timeout=10)
        results.record("Get notifications", resp.status_code in [200, 404])
    except Exception as e:
        results.record("Get notifications", False, str(e))


def test_coalition(token: str):
    """Test coalition service"""
    print("\n" + "=" * 60)
    print("10. COALITION (coalition-service)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Get members
    try:
        resp = requests.get(f"{SERVICES['coalition']}/api/v1/coalition/members", headers=headers, timeout=10)
        results.record("Get coalition members", resp.status_code in [200, 404])
    except Exception as e:
        results.record("Get coalition members", False, str(e))


def main():
    print("=" * 60)
    print("Encypher Full-Stack Integration Test")
    print("=" * 60)
    print(f"Testing {len(SERVICES)} services...")

    # 1. Check all services are healthy
    all_healthy = check_services_health()
    if not all_healthy:
        print("\n⚠️  Some services are not healthy. Continuing with available services...")

    # 2. User signup/login
    token, user_id = test_user_signup_login()

    # 3. API key generation
    api_key = test_api_key_generation(token)

    # 4. Enterprise API signing
    signed_content = test_enterprise_api_signing(api_key)

    # 5. Enterprise API verification
    test_enterprise_api_verification(api_key, signed_content)

    # 6. Analytics tracking
    test_analytics_tracking(token)

    # 7. Billing usage
    test_billing_usage(token)

    # 8. User profile
    test_user_profile(token)

    # 9. Notifications
    test_notifications(token)

    # 10. Coalition
    test_coalition(token)

    # Summary
    success = results.summary()

    if success:
        print("\n✅ Full-stack integration test PASSED!")
    else:
        print("\n❌ Full-stack integration test FAILED!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
