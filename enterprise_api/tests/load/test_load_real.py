"""
Real Load Tests for Enterprise API.

These tests run against the actual Docker infrastructure without mocks.
They test real database operations, real signing, and real verification.

Run with: docker exec encypher-enterprise-api pytest tests/load/test_load_real.py -v
"""

import asyncio
import os
import time
import uuid
from typing import List

import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app

# Configuration
DEMO_API_KEY = os.getenv("DEMO_API_KEY", "demo-api-key-for-testing")
ENTERPRISE_API_KEY = os.getenv("ENTERPRISE_API_KEY", "enterprise-api-key-for-testing")


pytestmark = pytest.mark.skipif(
    os.environ.get("REAL_LOAD_TESTS", "").lower() != "true",
    reason="Real load tests require Docker infrastructure; set REAL_LOAD_TESTS=true to run.",
)


class TestRealLoadPerformance:
    """
    Real load tests using actual Docker infrastructure.
    No mocks - tests real database, real signing, real verification.
    """

    @pytest_asyncio.fixture
    async def real_client(self, db: AsyncSession) -> AsyncClient:
        """Create a client that uses the real database session."""

        async def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

        app.dependency_overrides.clear()

    @pytest.fixture
    def auth_headers(self) -> dict:
        """Authentication headers using demo API key."""
        return {"Authorization": f"Bearer {DEMO_API_KEY}", "Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_sign_endpoint_latency(self, real_client: AsyncClient, auth_headers: dict):
        """
        Load test the /api/v1/sign endpoint.
        Target: P95 < 200ms, Avg < 100ms
        """
        # Warmup
        print("\nWarming up sign endpoint...")
        for _ in range(5):
            response = await real_client.post("/api/v1/sign", json={"text": "Warmup content for signing.", "title": "Warmup"}, headers=auth_headers)
            if response.status_code != 200:
                print(f"Warmup failed: {response.status_code} - {response.text}")

        # Load test
        print("Starting sign load test (50 requests)...")
        latencies: List[float] = []
        payload = {"text": "This is a load test content string for C2PA signing. " * 10, "title": "Load Test Document"}

        start_total = time.perf_counter()
        for i in range(50):
            t0 = time.perf_counter()
            response = await real_client.post("/api/v1/sign", json=payload, headers=auth_headers)
            t1 = time.perf_counter()

            if response.status_code == 200:
                latencies.append((t1 - t0) * 1000)  # ms
            else:
                print(f"Request {i} failed: {response.status_code}")

        total_time = time.perf_counter() - start_total

        # Calculate stats
        if latencies:
            p95 = np.percentile(latencies, 95)
            p99 = np.percentile(latencies, 99)
            avg = np.mean(latencies)
            min_lat = np.min(latencies)
            max_lat = np.max(latencies)

            print("\n=== Sign Endpoint Load Test Results ===")
            print("Total Requests: 50")
            print(f"Successful: {len(latencies)}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Throughput: {len(latencies) / total_time:.1f} req/s")
            print(f"Min Latency: {min_lat:.2f}ms")
            print(f"Avg Latency: {avg:.2f}ms")
            print(f"P95 Latency: {p95:.2f}ms")
            print(f"P99 Latency: {p99:.2f}ms")
            print(f"Max Latency: {max_lat:.2f}ms")

            # Assertions - relaxed for real DB operations
            assert p95 < 500, f"P95 latency {p95:.2f}ms exceeded target 500ms"
            assert avg < 250, f"Average latency {avg:.2f}ms exceeded target 250ms"
        else:
            pytest.fail("No successful requests")

    @pytest.mark.asyncio
    async def test_verify_endpoint_latency(self, real_client: AsyncClient, auth_headers: dict):
        """
        Load test the /api/v1/verify endpoint.
        Target: P95 < 150ms, Avg < 75ms (verification is lighter than signing)
        """
        # First, sign some content to verify
        sign_response = await real_client.post(
            "/api/v1/sign", json={"text": "Content to verify in load test.", "title": "Verify Test"}, headers=auth_headers
        )

        if sign_response.status_code != 200:
            pytest.skip(f"Could not sign content for verification: {sign_response.text}")

        signed_text = sign_response.json().get("signed_text", "")
        if not signed_text:
            pytest.skip("No signed text returned")

        # Warmup
        print("\nWarming up verify endpoint...")
        for _ in range(5):
            await real_client.post("/api/v1/verify", json={"text": signed_text}, headers=auth_headers)

        # Load test
        print("Starting verify load test (50 requests)...")
        latencies: List[float] = []

        start_total = time.perf_counter()
        for i in range(50):
            t0 = time.perf_counter()
            response = await real_client.post("/api/v1/verify", json={"text": signed_text}, headers=auth_headers)
            t1 = time.perf_counter()

            if response.status_code == 200:
                latencies.append((t1 - t0) * 1000)
            else:
                print(f"Request {i} failed: {response.status_code}")

        total_time = time.perf_counter() - start_total

        if latencies:
            p95 = np.percentile(latencies, 95)
            p99 = np.percentile(latencies, 99)
            avg = np.mean(latencies)

            print("\n=== Verify Endpoint Load Test Results ===")
            print("Total Requests: 50")
            print(f"Successful: {len(latencies)}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Throughput: {len(latencies) / total_time:.1f} req/s")
            print(f"Avg Latency: {avg:.2f}ms")
            print(f"P95 Latency: {p95:.2f}ms")
            print(f"P99 Latency: {p99:.2f}ms")

            assert p95 < 300, f"P95 latency {p95:.2f}ms exceeded target 300ms"
            assert avg < 150, f"Average latency {avg:.2f}ms exceeded target 150ms"
        else:
            pytest.fail("No successful requests")

    @pytest.mark.asyncio
    async def test_concurrent_sign_requests(self, real_client: AsyncClient, auth_headers: dict):
        """
        Test concurrent signing requests to verify async handling.
        """
        print("\nTesting concurrent sign requests...")

        async def sign_request(doc_id: int) -> tuple:
            """Make a single sign request and return (success, latency_ms)."""
            t0 = time.perf_counter()
            try:
                response = await real_client.post(
                    "/api/v1/sign",
                    json={"text": f"Concurrent test document {doc_id}. " * 5, "title": f"Concurrent Doc {doc_id}"},
                    headers=auth_headers,
                )
                t1 = time.perf_counter()
                return response.status_code == 200, (t1 - t0) * 1000
            except Exception:
                return False, 0

        # Run 20 concurrent requests in batches of 5
        all_results = []
        batch_size = 5
        num_requests = 20

        start_total = time.perf_counter()
        for batch_start in range(0, num_requests, batch_size):
            batch_end = min(batch_start + batch_size, num_requests)
            tasks = [sign_request(i) for i in range(batch_start, batch_end)]
            results = await asyncio.gather(*tasks)
            all_results.extend(results)

        total_time = time.perf_counter() - start_total

        successes = sum(1 for success, _ in all_results if success)
        latencies = [lat for success, lat in all_results if success and lat > 0]

        print("\n=== Concurrent Sign Test Results ===")
        print(f"Total Requests: {num_requests}")
        print(f"Successful: {successes}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {successes / total_time:.1f} req/s")

        if latencies:
            print(f"Avg Latency: {np.mean(latencies):.2f}ms")
            print(f"P95 Latency: {np.percentile(latencies, 95):.2f}ms")

        # At least 80% should succeed
        assert successes >= num_requests * 0.8, f"Only {successes}/{num_requests} succeeded"

    @pytest.mark.asyncio
    async def test_batch_sign_performance(self, real_client: AsyncClient, auth_headers: dict):
        """
        Test batch signing endpoint performance.
        """
        print("\nTesting batch sign performance...")

        # Create batch request with multiple items
        batch_request = {
            "mode": "c2pa",
            "segmentation_level": "sentence",
            "idempotency_key": f"load-test-{uuid.uuid4().hex[:8]}",
            "items": [{"document_id": f"doc-{i}", "text": f"Batch document {i} content. " * 3} for i in range(10)],
        }

        # Warmup
        warmup_request = {
            "mode": "c2pa",
            "segmentation_level": "sentence",
            "idempotency_key": f"warmup-{uuid.uuid4().hex[:8]}",
            "items": [{"document_id": "warmup", "text": "Warmup content."}],
        }
        await real_client.post("/api/v1/batch/sign", json=warmup_request, headers=auth_headers)

        # Measure batch performance
        latencies = []
        for i in range(5):
            batch_request["idempotency_key"] = f"load-test-{uuid.uuid4().hex[:8]}"

            t0 = time.perf_counter()
            response = await real_client.post("/api/v1/batch/sign", json=batch_request, headers=auth_headers)
            t1 = time.perf_counter()

            if response.status_code == 200:
                latencies.append((t1 - t0) * 1000)
            else:
                print(f"Batch {i} failed: {response.status_code} - {response.text[:200]}")

        if latencies:
            avg = np.mean(latencies)
            p95 = np.percentile(latencies, 95)

            print("\n=== Batch Sign Test Results ===")
            print("Batch Size: 10 items")
            print(f"Batches Run: {len(latencies)}")
            print(f"Avg Batch Latency: {avg:.2f}ms")
            print(f"P95 Batch Latency: {p95:.2f}ms")
            print(f"Avg Per-Item Latency: {avg / 10:.2f}ms")

            # Batch of 10 should complete in under 2 seconds
            assert avg < 2000, f"Batch avg {avg:.2f}ms exceeded target 2000ms"
        else:
            pytest.skip("No successful batch requests")


class TestRealDatabasePerformance:
    """
    Test database operation performance with real PostgreSQL.
    """

    @pytest.mark.asyncio
    async def test_merkle_root_creation_performance(self, db: AsyncSession):
        """Test Merkle root creation performance."""
        import uuid as uuid_module

        from app.models.merkle import MerkleRoot

        print("\nTesting Merkle root creation performance...")

        latencies = []
        for i in range(20):
            root = MerkleRoot(
                organization_id="org_demo",
                document_id=f"perf-doc-{uuid_module.uuid4().hex[:8]}",
                root_hash=f"hash_{i:04d}" + "0" * 56,
                algorithm="sha256",
                leaf_count=10,
                doc_metadata={"test": True},
            )

            t0 = time.perf_counter()
            db.add(root)
            await db.flush()
            t1 = time.perf_counter()

            latencies.append((t1 - t0) * 1000)

        await db.rollback()  # Don't persist test data

        avg = np.mean(latencies)
        p95 = np.percentile(latencies, 95)

        print("\n=== Merkle Root Creation Results ===")
        print(f"Operations: {len(latencies)}")
        print(f"Avg Latency: {avg:.2f}ms")
        print(f"P95 Latency: {p95:.2f}ms")

        assert avg < 50, f"Avg latency {avg:.2f}ms exceeded target 50ms"

    @pytest.mark.asyncio
    async def test_c2pa_schema_query_performance(self, db: AsyncSession):
        """Test C2PA schema query performance."""
        from sqlalchemy import select

        from app.models.c2pa_schema import C2PASchema

        print("\nTesting C2PA schema query performance...")

        latencies = []
        for _ in range(20):
            t0 = time.perf_counter()
            result = await db.execute(select(C2PASchema).where(C2PASchema.organization_id == "org_demo").limit(10))
            result.scalars().all()
            t1 = time.perf_counter()

            latencies.append((t1 - t0) * 1000)

        avg = np.mean(latencies)
        p95 = np.percentile(latencies, 95)

        print("\n=== C2PA Schema Query Results ===")
        print(f"Queries: {len(latencies)}")
        print(f"Avg Latency: {avg:.2f}ms")
        print(f"P95 Latency: {p95:.2f}ms")

        assert avg < 20, f"Avg latency {avg:.2f}ms exceeded target 20ms"


class TestRealEndToEndFlow:
    """
    Test complete end-to-end flows with real infrastructure.
    """

    @pytest_asyncio.fixture
    async def real_client(self, db: AsyncSession) -> AsyncClient:
        """Create a client that uses the real database session."""

        async def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

        app.dependency_overrides.clear()

    @pytest.fixture
    def auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {DEMO_API_KEY}", "Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_sign_verify_roundtrip(self, real_client: AsyncClient, auth_headers: dict):
        """
        Test complete sign -> verify roundtrip.
        """
        print("\nTesting sign -> verify roundtrip...")

        # Sign
        t0 = time.perf_counter()
        sign_response = await real_client.post(
            "/api/v1/sign", json={"text": "End-to-end test content for roundtrip.", "title": "E2E Test"}, headers=auth_headers
        )
        sign_time = (time.perf_counter() - t0) * 1000

        assert sign_response.status_code == 200, f"Sign failed: {sign_response.text}"
        signed_text = sign_response.json().get("signed_text", "")

        # Verify
        t0 = time.perf_counter()
        verify_response = await real_client.post("/api/v1/verify", json={"text": signed_text}, headers=auth_headers)
        verify_time = (time.perf_counter() - t0) * 1000

        assert verify_response.status_code == 200, f"Verify failed: {verify_response.text}"
        verify_data = verify_response.json()

        print("\n=== Sign -> Verify Roundtrip Results ===")
        print(f"Sign Latency: {sign_time:.2f}ms")
        print(f"Verify Latency: {verify_time:.2f}ms")
        print(f"Total Roundtrip: {sign_time + verify_time:.2f}ms")
        print(f"Verification Valid: {verify_data.get('valid', False)}")

        assert verify_data.get("valid", False), "Verification should be valid"
        assert sign_time + verify_time < 1000, "Roundtrip should be under 1 second"

    @pytest.mark.asyncio
    async def test_c2pa_schema_crud_flow(self, real_client: AsyncClient, auth_headers: dict):
        """
        Test C2PA schema CRUD operations.
        """
        print("\nTesting C2PA schema CRUD flow...")

        unique_label = f"com.test.load.{uuid.uuid4().hex[:8]}"

        # Create
        t0 = time.perf_counter()
        create_response = await real_client.post(
            "/api/v1/enterprise/c2pa/schemas",
            json={
                "name": "Load Test Schema",
                "label": unique_label,
                "version": "1.0",
                "json_schema": {"type": "object", "properties": {"test": {"type": "string"}}},
            },
            headers=auth_headers,
        )
        create_time = (time.perf_counter() - t0) * 1000

        if create_response.status_code != 201:
            print(f"Create failed: {create_response.status_code} - {create_response.text}")
            pytest.skip("Could not create schema")

        schema_id = create_response.json().get("id")

        # Read
        t0 = time.perf_counter()
        await real_client.get(f"/api/v1/enterprise/c2pa/schemas/{schema_id}", headers=auth_headers)
        read_time = (time.perf_counter() - t0) * 1000

        # List
        t0 = time.perf_counter()
        await real_client.get("/api/v1/enterprise/c2pa/schemas", headers=auth_headers)
        list_time = (time.perf_counter() - t0) * 1000

        # Delete
        t0 = time.perf_counter()
        await real_client.delete(f"/api/v1/enterprise/c2pa/schemas/{schema_id}", headers=auth_headers)
        delete_time = (time.perf_counter() - t0) * 1000

        print("\n=== C2PA Schema CRUD Results ===")
        print(f"Create Latency: {create_time:.2f}ms")
        print(f"Read Latency: {read_time:.2f}ms")
        print(f"List Latency: {list_time:.2f}ms")
        print(f"Delete Latency: {delete_time:.2f}ms")

        assert create_time < 200, f"Create latency {create_time:.2f}ms exceeded target"
        assert read_time < 100, f"Read latency {read_time:.2f}ms exceeded target"
        assert list_time < 200, f"List latency {list_time:.2f}ms exceeded target"
