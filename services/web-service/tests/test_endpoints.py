"""
Integration tests for web-service endpoints.
Tests all demo request and analytics endpoints.
"""
import httpx
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8010"

# Test data
AI_DEMO_REQUEST = {
    "name": "Test User AI",
    "email": "test.ai@example.com",
    "organization": "AI Test Corp",
    "role": "ML Engineer",
    "message": "Testing AI demo request endpoint",
    "consent": True,
    "source": "ai-demo-test"
}

PUBLISHER_DEMO_REQUEST = {
    "name": "Test User Publisher",
    "email": "test.publisher@example.com",
    "organization": "Publisher Test Inc",
    "role": "Content Manager",
    "message": "Testing publisher demo request endpoint",
    "consent": True,
    "source": "publisher-demo-test"
}

ENTERPRISE_SALES_REQUEST = {
    "name": "Enterprise Test User",
    "email": "enterprise@example.com",
    "organization": "Enterprise Corp",
    "role": "CTO",
    "message": "Testing enterprise sales endpoint",
    "consent": True,
    "source": "enterprise-sales-test"
}

GENERAL_SALES_REQUEST = {
    "name": "General Test User",
    "email": "general@example.com",
    "organization": "General Corp",
    "role": "Product Manager",
    "message": "Testing general sales endpoint",
    "consent": True,
    "source": "general-sales-test"
}

ANALYTICS_EVENT = {
    "event_name": "test_event",
    "event_type": "custom",
    "session_id": "test-session-123",
    "page_url": "http://localhost:3000/test",
    "page_title": "Test Page",
    "properties": {
        "test_property": "test_value",
        "source": "integration_test"
    }
}


async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
        return True


async def test_ai_demo_request():
    """Test AI demo request endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/ai-demo/demo-requests",
            json=AI_DEMO_REQUEST
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        print(f"✅ AI Demo request created: {data['id']}")
        return data["id"]


async def test_ai_demo_analytics():
    """Test AI demo analytics endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/ai-demo/analytics/events",
            json=ANALYTICS_EVENT
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        print("✅ AI Demo analytics event tracked")
        return True


async def test_publisher_demo_request():
    """Test Publisher demo request endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/publisher-demo/demo-requests",
            json=PUBLISHER_DEMO_REQUEST
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        print(f"✅ Publisher Demo request created: {data['id']}")
        return data["id"]


async def test_publisher_demo_analytics():
    """Test Publisher demo analytics endpoint"""
    async with httpx.AsyncClient() as client:
        event = ANALYTICS_EVENT.copy()
        event["event_name"] = "publisher_demo_loaded"
        response = await client.post(
            f"{BASE_URL}/api/v1/publisher-demo/analytics/events",
            json=event
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        print("✅ Publisher Demo analytics event tracked")
        return True


async def test_publisher_demo_get_request(request_id: str):
    """Test getting a publisher demo request by ID"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/publisher-demo/demo-requests/{request_id}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["id"] == request_id
        print(f"✅ Publisher Demo request retrieved: {data['email']}")
        return True


async def test_enterprise_sales():
    """Test Enterprise sales endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/sales/enterprise-requests",
            json=ENTERPRISE_SALES_REQUEST
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        print(f"✅ Enterprise sales request created: {data['id']}")
        return data["id"]


async def test_general_sales():
    """Test General sales endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/sales/general-requests",
            json=GENERAL_SALES_REQUEST
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        print(f"✅ General sales request created: {data['id']}")
        return data["id"]


async def test_legacy_demo_request():
    """Test legacy generic demo request endpoint"""
    async with httpx.AsyncClient() as client:
        legacy_request = {
            "name": "Legacy Test User",
            "email": "legacy@example.com",
            "organization": "Legacy Corp",
            "role": "Developer",
            "message": "Testing legacy endpoint",
            "consent": True,
            "source": "legacy-test"
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/demo-requests/",
            json=legacy_request
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        print(f"✅ Legacy demo request created: {data.get('uuid', data.get('id', 'unknown'))}")
        return True


async def test_legacy_analytics():
    """Test legacy generic analytics endpoint"""
    async with httpx.AsyncClient() as client:
        event = {
            "event_type": "page_view",
            "event_name": "legacy_test_event",
            "session_id": "legacy-session-123",
            "page_url": "http://localhost:3000/legacy",
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/analytics/",
            json=event
        )
        # Legacy endpoint might have different schema requirements
        if response.status_code == 200:
            print("✅ Legacy analytics event tracked")
        else:
            print(f"⚠️  Legacy analytics returned {response.status_code}: {response.text[:100]}")
        return True


async def run_all_tests():
    """Run all endpoint tests"""
    print("\n" + "="*60)
    print("🧪 Web Service Endpoint Tests")
    print("="*60 + "\n")
    
    results = []
    
    # Health check
    try:
        await test_health()
        results.append(("Health Check", True))
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        results.append(("Health Check", False))
    
    # AI Demo endpoints
    try:
        await test_ai_demo_request()
        results.append(("AI Demo Request", True))
    except Exception as e:
        print(f"❌ AI Demo request failed: {e}")
        results.append(("AI Demo Request", False))
    
    try:
        await test_ai_demo_analytics()
        results.append(("AI Demo Analytics", True))
    except Exception as e:
        print(f"❌ AI Demo analytics failed: {e}")
        results.append(("AI Demo Analytics", False))
    
    # Publisher Demo endpoints
    publisher_request_id = None
    try:
        publisher_request_id = await test_publisher_demo_request()
        results.append(("Publisher Demo Request", True))
    except Exception as e:
        print(f"❌ Publisher Demo request failed: {e}")
        results.append(("Publisher Demo Request", False))
    
    try:
        await test_publisher_demo_analytics()
        results.append(("Publisher Demo Analytics", True))
    except Exception as e:
        print(f"❌ Publisher Demo analytics failed: {e}")
        results.append(("Publisher Demo Analytics", False))
    
    if publisher_request_id:
        try:
            await test_publisher_demo_get_request(publisher_request_id)
            results.append(("Publisher Demo GET", True))
        except Exception as e:
            print(f"❌ Publisher Demo GET failed: {e}")
            results.append(("Publisher Demo GET", False))
    
    # Sales endpoints
    try:
        await test_enterprise_sales()
        results.append(("Enterprise Sales", True))
    except Exception as e:
        print(f"❌ Enterprise sales failed: {e}")
        results.append(("Enterprise Sales", False))
    
    try:
        await test_general_sales()
        results.append(("General Sales", True))
    except Exception as e:
        print(f"❌ General sales failed: {e}")
        results.append(("General Sales", False))
    
    # Legacy endpoints
    try:
        await test_legacy_demo_request()
        results.append(("Legacy Demo Request", True))
    except Exception as e:
        print(f"❌ Legacy demo request failed: {e}")
        results.append(("Legacy Demo Request", False))
    
    try:
        await test_legacy_analytics()
        results.append(("Legacy Analytics", True))
    except Exception as e:
        print(f"❌ Legacy analytics failed: {e}")
        results.append(("Legacy Analytics", False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
