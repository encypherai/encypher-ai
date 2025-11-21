import pytest
import httpx
import asyncio
import time
import docker
import os
import socket
import numpy as np
import subprocess
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Check if docker is available
try:
    docker_client = docker.from_env()
    docker_client.ping()
    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
class TestLoadDockerIntegration:
    
    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Start Postgres container."""
        container = docker_client.containers.run(
            "postgres:15-alpine",
            environment={
                "POSTGRES_USER": "encypher",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "encypher_test"
            },
            ports={'5432/tcp': 54321},
            detach=True,
            remove=True
        )
        
        db_url = "postgresql+asyncpg://encypher:password@localhost:54321/encypher_test"
        
        # Wait for ready
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                with socket.create_connection(("localhost", 54321), timeout=1):
                    break
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(1)
        
        yield container, db_url
        container.stop()

    def test_load_performance(self, postgres_container):
        """
        True integration load test.
        Starts App (Uvicorn) -> Connects to Docker DB.
        Client -> Hits App -> Measures Latency.
        """
        container, db_url = postgres_container
        server_port = 8091
        
        # 1. Init DB Schema
        async def init_db():
            engine = create_async_engine(db_url)
            async with engine.begin() as conn:
                with open("scripts/init_db.sql", "r") as f:
                    schema_sql = f.read()
                    for statement in schema_sql.split(';'):
                        if statement.strip():
                            await conn.execute(text(statement))
            await engine.dispose()
        
        asyncio.run(init_db())
        
        # 2. Start Server using Subprocess
        env = os.environ.copy()
        env["DATABASE_URL"] = db_url.replace("+asyncpg", "")
        env["KEY_ENCRYPTION_KEY"] = "00" * 32
        env["ENCRYPTION_NONCE"] = "00" * 12
        env["SSL_COM_API_KEY"] = "test_key"
        env["DEMO_API_KEY"] = "demo-key-load-test"
        env["PORT"] = str(server_port)
        
        # Path to run_server.py
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_server.py")
        
        proc = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        try:
            # Wait for server to start
            base_url = f"http://127.0.0.1:{server_port}"
            start_time = time.time()
            server_up = False
            while time.time() - start_time < 10:
                try:
                    httpx.get(f"{base_url}/health")
                    server_up = True
                    break
                except (httpx.ConnectError, httpx.ReadTimeout):
                    time.sleep(0.5)
            
            if not server_up:
                # If failed, try to get output from a retry or log file
                # But for now just fail
                pytest.fail("Server failed to start (check logs)")

            # 3. Run Load Test
            print("\nStarting load test against running server...")
            
            latencies = []
            payload = {"text": "This is a load test content string." * 10, "title": "Load Test"}
            # Using demo key to bypass auth service dependency
            headers = {"Authorization": "Bearer demo-key-load-test"}
            
            # Warmup
            for _ in range(5):
                resp = httpx.post(f"{base_url}/api/v1/sign", json=payload, headers=headers)
                assert resp.status_code == 200
            
            # Measure
            start_total = time.time()
            for _ in range(50):
                t0 = time.time()
                resp = httpx.post(f"{base_url}/api/v1/sign", json=payload, headers=headers)
                t1 = time.time()
                assert resp.status_code == 200
                latencies.append((t1 - t0) * 1000)
            
            total_time = time.time() - start_total
            
            # Stats
            p95 = np.percentile(latencies, 95)
            avg = np.mean(latencies)
            
            print(f"\nResults: Avg={avg:.2f}ms, P95={p95:.2f}ms")
            
            assert p95 < 100, f"P95 {p95}ms too high"
            assert avg < 50, f"Avg {avg}ms too high"
            
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
