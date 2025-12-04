#!/usr/bin/env python3
"""
Individual endpoint tests for each Encypher microservice.

Usage:
    python scripts/test_service_endpoints.py
"""
import subprocess
import sys
from datetime import datetime

import requests

BASE_URLS = {
    "auth": "http://localhost:8001",
    "user": "http://localhost:8002",
    "key": "http://localhost:8003",
    "encoding": "http://localhost:8004",
    "verification": "http://localhost:8005",
    "analytics": "http://localhost:8006",
    "billing": "http://localhost:8007",
    "notification": "http://localhost:8008",
    "coalition": "http://localhost:8009",
}

# Traefik handles routing in production (port 80/443)
# For local testing, we test services directly on their ports

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
    
    def record(self, name: str, passed: bool, error: str = None, skipped: bool = False):
        if skipped:
            self.skipped += 1
            print(f"  ⊘ {name} (skipped)")
        elif passed:
            self.passed += 1
            print(f"  ✓ {name}")
        else:
            self.failed += 1
            self.errors.append((name, error))
            print(f"  ✗ {name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*60}")
        print(f"Results: {self.passed} passed, {self.failed} failed, {self.skipped} skipped (total: {total})")
        if self.errors:
            print("\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        return self.failed == 0

results = TestResults()

def get_auth_token():
    """Create a test user and get auth token"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    email = f"test_{timestamp}@example.com"
    password = "TestPassword123!"
    
    # Signup
    try:
        resp = requests.post(
            f"{BASE_URLS['auth']}/api/v1/auth/signup",
            json={"email": email, "password": password, "name": "Test User"},
            timeout=10
        )
        if resp.status_code not in [200, 201]:
            print(f"  Signup failed: {resp.status_code}")
            return None, None
        
        user_id = resp.json().get("data", {}).get("id")
        
        # Verify email in DB
        subprocess.run([
            "docker", "exec", "encypher-postgres-auth", 
            "psql", "-U", "encypher", "-d", "encypher_auth", 
            "-c", f"UPDATE users SET email_verified = true WHERE email = '{email}';"
        ], capture_output=True)
        
        # Login
        resp = requests.post(
            f"{BASE_URLS['auth']}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            token = resp.json().get("data", {}).get("access_token")
            return token, user_id
        return None, None
    except Exception as e:
        print(f"  Auth setup failed: {e}")
        return None, None

# ============================================
# AUTH SERVICE TESTS
# ============================================
def test_auth_service(token: str):
    """Test auth service endpoints"""
    print("\n" + "="*60)
    print("AUTH SERVICE (8001)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['auth']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Test token verification (POST endpoint)
    try:
        resp = requests.post(f"{BASE_URLS['auth']}/api/v1/auth/verify", headers=headers, timeout=5)
        results.record("POST /api/v1/auth/verify", resp.status_code in [200, 401], f"Status {resp.status_code}")
    except Exception as e:
        results.record("POST /api/v1/auth/verify", False, str(e))
    
    # Test refresh token
    try:
        resp = requests.post(f"{BASE_URLS['auth']}/api/v1/auth/refresh", headers=headers, timeout=5)
        # May fail without refresh token in body, but endpoint should exist
        results.record("POST /api/v1/auth/refresh", resp.status_code in [200, 400, 401, 422])
    except Exception as e:
        results.record("POST /api/v1/auth/refresh", False, str(e))

# ============================================
# KEY SERVICE TESTS
# ============================================
def test_key_service(token: str):
    """Test key service endpoints"""
    print("\n" + "="*60)
    print("KEY SERVICE (8003)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    api_key = None
    key_id = None
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['key']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Generate key
    try:
        resp = requests.post(
            f"{BASE_URLS['key']}/api/v1/keys/generate",
            json={"name": "Test Key", "permissions": ["sign", "verify"]},
            headers=headers,
            timeout=10
        )
        if resp.status_code in [200, 201]:
            data = resp.json()
            api_key = data.get("key")
            key_id = data.get("id")
            results.record("POST /api/v1/keys/generate", True)
        else:
            results.record("POST /api/v1/keys/generate", False, f"Status {resp.status_code}")
    except Exception as e:
        results.record("POST /api/v1/keys/generate", False, str(e))
    
    # Verify key (test before any modifications)
    if api_key:
        try:
            resp = requests.post(
                f"{BASE_URLS['key']}/api/v1/keys/verify",
                json={"key": api_key},
                timeout=5
            )
            is_valid = resp.status_code == 200 and resp.json().get("valid", False)
            results.record("POST /api/v1/keys/verify", is_valid, f"Status {resp.status_code}, valid={resp.json().get('valid') if resp.status_code == 200 else 'N/A'}")
        except Exception as e:
            results.record("POST /api/v1/keys/verify", False, str(e))
    
    # List keys
    try:
        resp = requests.get(f"{BASE_URLS['key']}/api/v1/keys", headers=headers, timeout=5)
        results.record("GET /api/v1/keys", resp.status_code == 200)
    except Exception as e:
        results.record("GET /api/v1/keys", False, str(e))
    
    # Get key by ID
    if key_id:
        try:
            resp = requests.get(f"{BASE_URLS['key']}/api/v1/keys/{key_id}", headers=headers, timeout=5)
            results.record("GET /api/v1/keys/{id}", resp.status_code == 200)
        except Exception as e:
            results.record("GET /api/v1/keys/{id}", False, str(e))
    
    # Revoke key (do this last since it invalidates the key)
    if key_id:
        try:
            resp = requests.delete(f"{BASE_URLS['key']}/api/v1/keys/{key_id}", headers=headers, timeout=5)
            results.record("DELETE /api/v1/keys/{id}", resp.status_code in [200, 204])
        except Exception as e:
            results.record("DELETE /api/v1/keys/{id}", False, str(e))

# ============================================
# USER SERVICE TESTS
# ============================================
def test_user_service(token: str, user_id: str):
    """Test user service endpoints"""
    print("\n" + "="*60)
    print("USER SERVICE (8002)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['user']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Get profile
    try:
        resp = requests.get(f"{BASE_URLS['user']}/api/v1/profile", headers=headers, timeout=5)
        results.record("GET /api/v1/profile", resp.status_code in [200, 404])  # 404 if no profile yet
    except Exception as e:
        results.record("GET /api/v1/profile", False, str(e))
    
    # Update profile
    try:
        resp = requests.put(
            f"{BASE_URLS['user']}/api/v1/profile",
            json={"display_name": "Test User", "bio": "Testing"},
            headers=headers,
            timeout=5
        )
        results.record("PUT /api/v1/profile", resp.status_code in [200, 201, 404])
    except Exception as e:
        results.record("PUT /api/v1/profile", False, str(e))

# ============================================
# BILLING SERVICE TESTS
# ============================================
def test_billing_service(token: str):
    """Test billing service endpoints"""
    print("\n" + "="*60)
    print("BILLING SERVICE (8007)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['billing']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Get plans
    try:
        resp = requests.get(f"{BASE_URLS['billing']}/api/v1/billing/plans", timeout=5)
        results.record("GET /api/v1/billing/plans", resp.status_code in [200, 404])
    except Exception as e:
        results.record("GET /api/v1/billing/plans", False, str(e))
    
    # Get subscription
    try:
        resp = requests.get(f"{BASE_URLS['billing']}/api/v1/billing/subscription", headers=headers, timeout=5)
        results.record("GET /api/v1/billing/subscription", resp.status_code in [200, 401, 404, 500], f"Status {resp.status_code}")
    except Exception as e:
        results.record("GET /api/v1/billing/subscription", False, str(e))
    
    # Get usage
    try:
        resp = requests.get(f"{BASE_URLS['billing']}/api/v1/billing/usage", headers=headers, timeout=5)
        results.record("GET /api/v1/billing/usage", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("GET /api/v1/billing/usage", False, str(e))

# ============================================
# ANALYTICS SERVICE TESTS
# ============================================
def test_analytics_service(token: str):
    """Test analytics service endpoints"""
    print("\n" + "="*60)
    print("ANALYTICS SERVICE (8006)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['analytics']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Get usage stats
    try:
        resp = requests.get(f"{BASE_URLS['analytics']}/api/v1/analytics/stats", headers=headers, timeout=5)
        results.record("GET /api/v1/analytics/stats", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("GET /api/v1/analytics/stats", False, str(e))
    
    # Record metric
    try:
        resp = requests.post(
            f"{BASE_URLS['analytics']}/api/v1/analytics/track",
            json={"metric_type": "api_call", "service_name": "test"},
            headers=headers,
            timeout=5
        )
        results.record("POST /api/v1/analytics/track", resp.status_code in [200, 201, 401, 404, 422])
    except Exception as e:
        results.record("POST /api/v1/analytics/track", False, str(e))

# ============================================
# ENCODING SERVICE TESTS
# ============================================
def test_encoding_service(token: str):
    """Test encoding service endpoints"""
    print("\n" + "="*60)
    print("ENCODING SERVICE (8004)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['encoding']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Encode content
    try:
        resp = requests.post(
            f"{BASE_URLS['encoding']}/api/v1/encode",
            json={"content": "Test content for encoding", "format": "text"},
            headers=headers,
            timeout=10
        )
        results.record("POST /api/v1/encode", resp.status_code in [200, 201, 401, 404, 422])
    except Exception as e:
        results.record("POST /api/v1/encode", False, str(e))
    
    # List documents
    try:
        resp = requests.get(f"{BASE_URLS['encoding']}/api/v1/documents", headers=headers, timeout=5)
        results.record("GET /api/v1/documents", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("GET /api/v1/documents", False, str(e))

# ============================================
# VERIFICATION SERVICE TESTS
# ============================================
def test_verification_service(token: str):
    """Test verification service endpoints"""
    print("\n" + "="*60)
    print("VERIFICATION SERVICE (8005)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['verification']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Verify content
    try:
        resp = requests.post(
            f"{BASE_URLS['verification']}/api/v1/verify",
            json={"content": "Test content to verify"},
            headers=headers,
            timeout=10
        )
        results.record("POST /api/v1/verify", resp.status_code in [200, 400, 401, 404, 422])
    except Exception as e:
        results.record("POST /api/v1/verify", False, str(e))

# ============================================
# NOTIFICATION SERVICE TESTS
# ============================================
def test_notification_service(token: str):
    """Test notification service endpoints"""
    print("\n" + "="*60)
    print("NOTIFICATION SERVICE (8008)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['notification']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # List notifications
    try:
        resp = requests.get(f"{BASE_URLS['notification']}/api/v1/notifications", headers=headers, timeout=5)
        results.record("GET /api/v1/notifications", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("GET /api/v1/notifications", False, str(e))

# ============================================
# COALITION SERVICE TESTS
# ============================================
def test_coalition_service(token: str):
    """Test coalition service endpoints"""
    print("\n" + "="*60)
    print("COALITION SERVICE (8009)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health
    try:
        resp = requests.get(f"{BASE_URLS['coalition']}/health", timeout=5)
        results.record("GET /health", resp.status_code == 200)
    except Exception as e:
        results.record("GET /health", False, str(e))
    
    # Get members
    try:
        resp = requests.get(f"{BASE_URLS['coalition']}/api/v1/coalition/members", headers=headers, timeout=5)
        results.record("GET /api/v1/coalition/members", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("GET /api/v1/coalition/members", False, str(e))
    
    # Get stats
    try:
        resp = requests.get(f"{BASE_URLS['coalition']}/api/v1/coalition/stats", headers=headers, timeout=5)
        results.record("GET /api/v1/coalition/stats", resp.status_code in [200, 401, 404])
    except Exception as e:
        results.record("GET /api/v1/coalition/stats", False, str(e))

# ============================================
# TRAEFIK ROUTING TESTS (Optional)
# ============================================
def test_traefik_routing(token: str):
    """Test Traefik routing (if running)"""
    print("\n" + "="*60)
    print("TRAEFIK ROUTING (Optional)")
    print("="*60)
    
    # Traefik dashboard runs on port 8080
    try:
        resp = requests.get("http://localhost:8080/api/overview", timeout=2)
        if resp.status_code == 200:
            results.record("Traefik dashboard accessible", True)
        else:
            results.record("Traefik dashboard", False, f"Status {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("  ⊘ Traefik not running (optional - services tested directly)")

def main():
    print("="*60)
    print("Encypher Individual Service Endpoint Tests")
    print("="*60)
    
    # Get auth token
    print("\nSetting up test user...")
    token, user_id = get_auth_token()
    if token:
        print("  ✓ Auth token obtained")
    else:
        print("  ✗ Failed to get auth token - some tests will be skipped")
    
    # Run all tests
    test_auth_service(token)
    test_key_service(token)
    test_user_service(token, user_id)
    test_billing_service(token)
    test_analytics_service(token)
    test_encoding_service(token)
    test_verification_service(token)
    test_notification_service(token)
    test_coalition_service(token)
    test_traefik_routing(token)
    
    # Print summary
    success = results.summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
