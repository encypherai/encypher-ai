import pytest
import time
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Import app
from app.main import app
from app.models.organization import Organization

class TestLoadSimulation:
    
    def test_sign_endpoint_performance_cpu(self):
        """
        Load test the /sign endpoint to verify CPU performance and async architecture.
        Mocks Database I/O with fixed latency to simulate production DB.
        Verifies that Spacy segmentation and C2PA signing are efficient.
        """
        
        # Mock DB Session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock Organization fetch
        mock_org = {
            "api_key": "test_key",
            "organization_id": "org_sim_test",
            "organization_name": "Simulation Org",
            "tier": "enterprise",
            "can_sign": True,
            "can_verify": True,
            "monthly_quota": 100000,
            "api_calls_this_month": 0
        }
        
        # Mock Key Service Client
        mock_key_client = AsyncMock()
        mock_key_client.validate_key.return_value = mock_org
        
        # Mock Stat Service (Async)
        mock_stat_service = AsyncMock()
        
        # Mock DB execute results (for any other queries)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_result.fetchone.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Ensure modules are imported
        from app.services import key_service_client as ksc_module
        from app.services import stat_service as ss_module
        from app import database as db_module
        import app.dependencies as deps_module
        from sqlalchemy.ext.asyncio import AsyncEngine
        from app.services import signing_executor as se_module

        from app.database import get_db
        from cryptography.hazmat.primitives.asymmetric import ed25519
        import app.middleware.api_rate_limiter as limiter_module
        
        # Generate a dummy private key for signing
        dummy_private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Mock Rate Limiter
        mock_limiter_check = MagicMock(return_value=(True, None, 1000, 1000))
        
        # Apply patches
        with patch.object(ksc_module, "key_service_client", mock_key_client), \
             patch.object(deps_module, "key_service_client", mock_key_client), \
             patch.object(ss_module, "stat_service", mock_stat_service), \
             patch.object(db_module, "get_db", return_value=mock_db), \
             patch.object(deps_module, "get_db", return_value=mock_db), \
             patch.object(se_module, "load_organization_private_key", new_callable=AsyncMock) as mock_load_key, \
             patch.object(limiter_module.api_rate_limiter, "check", mock_limiter_check):
             
            mock_load_key.return_value = dummy_private_key
             
            # Note: app.database.get_db is a dependency, we need to override it in app.dependency_overrides
            async def override_get_db():
                # Simulate DB connection latency (pool checkout)
                await asyncio.sleep(0.001) 
                yield mock_db
                # Simulate commit latency
                await asyncio.sleep(0.002)
            
            app.dependency_overrides[get_db] = override_get_db
            
            # Simulate DB write latency in execute/commit
            async def simulate_db_io(*args, **kwargs):
                await asyncio.sleep(0.002) # 2ms write
                return mock_result
            
            mock_db.execute.side_effect = simulate_db_io
            mock_db.commit.side_effect = simulate_db_io
            
            # Run Load Test with TestClient (No context manager to skip lifespan startup)
            client = TestClient(app)
            
            print("\nWarming up...")
            for _ in range(10):
                resp = client.post(
                    "/api/v1/sign",
                    json={"text": "Warmup content " * 5, "title": "Warmup"},
                    headers={"Authorization": "Bearer test_key"}
                )
                assert resp.status_code == 200
            
            print("Starting simulation load test (100 requests)...")
            latencies = []
            payload = {"text": "This is a simulation load test content string." * 20, "title": "Simulation Load Test"}
            
            import time
            start_total = time.time()
            for i in range(100):
                t0 = time.time()
                resp = client.post(
                    "/api/v1/sign",
                    json=payload,
                    headers={"Authorization": "Bearer test_key"}
                )
                t1 = time.time()
                assert resp.status_code == 200
                latencies.append((t1 - t0) * 1000) # ms
            
            total_time = time.time() - start_total
            
            # Stats
            p95 = np.percentile(latencies, 95)
            avg = np.mean(latencies)
            
            print(f"\nSimulation Results:")
            print(f"Total Requests: 100")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Avg Latency: {avg:.2f}ms")
            print(f"P95 Latency: {p95:.2f}ms")
            
            # Clear overrides
            app.dependency_overrides = {}
            
            # Assertions
            # If Spacy was reloading, this would be > 300ms
            # Batch insert optimization brought this down to ~110ms in simulation
            assert p95 < 150, f"P95 latency {p95}ms exceeded target 150ms"
                
import asyncio
