import pytest
import asyncio
import time
import docker
import socket
import numpy as np
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from unittest.mock import patch, AsyncMock
from starlette.testclient import TestClient

# Import app components
from app.main import app

# Check if docker is available
try:
    docker_client = docker.from_env()
    docker_client.ping()
    DOCKER_AVAILABLE = True
except Exception as e:
    print(f"Docker check failed: {e}")
    DOCKER_AVAILABLE = False

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available or not running")
class TestLoadDocker:
    
    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Start a fresh Postgres container for load testing."""
        print("\nStarting Postgres container...")
        container = docker_client.containers.run(
            "postgres:15-alpine",
            environment={
                "POSTGRES_USER": "encypher",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "encypher_test"
            },
            ports={'5432/tcp': 54320},  # Use non-standard port to avoid conflict
            detach=True,
            remove=True
        )
        
        # Wait for Postgres to be ready
        db_url = "postgresql+asyncpg://encypher:password@localhost:54320/encypher_test"
        timeout = 30
        start_time = time.time()
        
        # Poll port first
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection(("localhost", 54320), timeout=1):
                    break
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(1)
        
        yield container, db_url
        
        print("\nStopping Postgres container...")
        container.stop()

    def test_sign_endpoint_latency(self, postgres_container):
        """
        Load test the /sign endpoint to ensure p95 latency < 100ms.
        Uses real Docker Postgres + Mocked Key Service.
        """
        container, db_url = postgres_container
        
        # 1. Configure App to use Docker DB
        # Create new engine and sessionmaker for the test DB
        test_engine = create_async_engine(db_url)
        test_session_factory = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        
        # 2. Initialize DB Schema (Async helper)
        async def init_db():
            async with test_engine.begin() as conn:
                # Read schema file
                try:
                    with open("scripts/init_db.sql", "r") as f:
                        schema_sql = f.read()
                        for statement in schema_sql.split(';'):
                            if statement.strip():
                                await conn.execute(text(statement))
                except FileNotFoundError:
                    pytest.fail("init_db.sql not found")

        # Run DB init
        asyncio.run(init_db())

        # 3. Mock Key Service Client (Cached response)
        mock_key_client = AsyncMock()
        mock_key_client.validate_key.return_value = {
            "api_key": "test_key_load",
            "organization_id": "org_load_test",
            "tier": "enterprise",
            "can_sign": True,
            "can_verify": True
        }
        
        # 4. Run Load Test
        # Patch dependencies AND Database Engine
        with patch("app.dependencies.key_service_client", mock_key_client), \
             patch("app.services.stat_service.stat_service.update_api_key_last_used", new_callable=AsyncMock), \
             patch("app.services.session_service.session_service.connect", new_callable=AsyncMock), \
             patch("app.services.session_service.session_service.disconnect", new_callable=AsyncMock), \
             patch("app.database.engine", test_engine), \
             patch("app.database.async_session_factory", test_session_factory):
            
            # Use TestClient (Sync)
            with TestClient(app) as client:
                
                # Warm up
                print("\nWarming up...")
                for _ in range(5):
                    resp = client.post(
                        "/api/v1/sign",
                        json={"text": "Warmup content", "title": "Warmup"},
                        headers={"Authorization": "Bearer test_key_load"}
                    )
                    assert resp.status_code == 200

                # Load Phase
                print("Starting load test (50 requests)...")
                latencies = []
                payload = {"text": "This is a load test content string." * 10, "title": "Load Test"}
                
                start_total = time.time()
                for i in range(50):
                    t0 = time.time()
                    resp = client.post(
                        "/api/v1/sign",
                        json=payload,
                        headers={"Authorization": "Bearer test_key_load"}
                    )
                    t1 = time.time()
                    assert resp.status_code == 200
                    latencies.append((t1 - t0) * 1000) # ms
                
                total_time = time.time() - start_total
                
                # Stats
                p95 = np.percentile(latencies, 95)
                avg = np.mean(latencies)
                p99 = np.percentile(latencies, 99)
                
                print("\nLoad Test Results:")
                print("Total Requests: 50")
                print(f"Total Time: {total_time:.2f}s")
                print(f"Avg Latency: {avg:.2f}ms")
                print(f"P95 Latency: {p95:.2f}ms")
                print(f"P99 Latency: {p99:.2f}ms")
                
                # Assertions
                assert p95 < 100, f"P95 latency {p95}ms exceeded target 100ms"
                assert avg < 50, f"Average latency {avg}ms exceeded target 50ms"
