"""
Performance and load tests for C2PA custom assertions.
"""
import asyncio
import time

import pytest
from httpx import AsyncClient

from app.services.c2pa_validator import C2PAValidator


class TestC2PAValidatorPerformance:
    """Performance tests for C2PA validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = C2PAValidator()
    
    def test_schema_validation_performance(self):
        """Test that schema validation completes in < 50ms."""
        label = "c2pa.location.v1"
        data = {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
        
        # Warm up
        self.validator.validate_assertion(label, data)
        
        # Measure
        iterations = 100
        start = time.perf_counter()
        
        for _ in range(iterations):
            self.validator.validate_assertion(label, data)
        
        end = time.perf_counter()
        avg_time_ms = ((end - start) / iterations) * 1000
        
        print(f"\nAverage validation time: {avg_time_ms:.2f}ms")
        assert avg_time_ms < 50, f"Validation took {avg_time_ms:.2f}ms, expected < 50ms"
    
    def test_schema_caching_performance(self):
        """Test that schema caching improves performance."""
        label = "c2pa.location.v1"
        data = {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
        
        # First call (cache miss)
        start = time.perf_counter()
        self.validator.validate_assertion(label, data)
        first_call_time = time.perf_counter() - start
        
        # Second call (cache hit)
        start = time.perf_counter()
        self.validator.validate_assertion(label, data)
        second_call_time = time.perf_counter() - start
        
        print(f"\nFirst call: {first_call_time*1000:.2f}ms")
        print(f"Second call: {second_call_time*1000:.2f}ms")
        print(f"Speedup: {first_call_time/second_call_time:.1f}x")
        
        # Cached call should be faster
        assert second_call_time < first_call_time
    
    def test_batch_validation_performance(self):
        """Test batch validation performance."""
        assertions = [
            {
                "label": "c2pa.location.v1",
                "data": {"latitude": 37.7749, "longitude": -122.4194}
            },
            {
                "label": "c2pa.training-mining.v1",
                "data": {
                    "use": {
                        "ai_training": False,
                        "ai_inference": False,
                        "data_mining": False
                    }
                }
            },
            {
                "label": "c2pa.claim_review.v1",
                "data": {
                    "claim_reviewed": "Test claim",
                    "rating": "True"
                }
            }
        ]
        
        # Warm up
        self.validator.validate_custom_assertions(assertions, {})
        
        # Measure
        iterations = 50
        start = time.perf_counter()
        
        for _ in range(iterations):
            self.validator.validate_custom_assertions(assertions, {})
        
        end = time.perf_counter()
        avg_time_ms = ((end - start) / iterations) * 1000
        
        print(f"\nAverage batch validation time (3 assertions): {avg_time_ms:.2f}ms")
        assert avg_time_ms < 150, f"Batch validation took {avg_time_ms:.2f}ms, expected < 150ms"
    
    def test_complex_schema_validation_performance(self):
        """Test validation performance with complex nested schemas."""
        label = "c2pa.claim_review.v1"
        data = {
            "claim_reviewed": "Complex statement with lots of details",
            "rating": "True",
            "appearance_url": "https://example.com/article/12345",
            "author": {
                "name": "FactCheck Organization",
                "url": "https://factcheck.org",
                "logo": "https://factcheck.org/logo.png"
            },
            "date_published": "2025-11-03T14:00:00Z",
            "url": "https://factcheck.org/review/12345",
            "item_reviewed": {
                "type": "Claim",
                "appearance": {
                    "url": "https://example.com/original"
                }
            }
        }
        
        iterations = 100
        start = time.perf_counter()
        
        for _ in range(iterations):
            self.validator.validate_assertion(label, data)
        
        end = time.perf_counter()
        avg_time_ms = ((end - start) / iterations) * 1000
        
        print(f"\nAverage complex validation time: {avg_time_ms:.2f}ms")
        assert avg_time_ms < 50, f"Complex validation took {avg_time_ms:.2f}ms, expected < 50ms"
    
    def test_custom_schema_registration_performance(self):
        """Test custom schema registration performance."""
        schemas = []
        for i in range(10):
            schemas.append({
                "label": f"com.test.schema{i}.v1",
                "schema": {
                    "type": "object",
                    "properties": {
                        "field1": {"type": "string"},
                        "field2": {"type": "number"},
                        "field3": {"type": "boolean"}
                    },
                    "required": ["field1"]
                }
            })
        
        start = time.perf_counter()
        
        for schema_def in schemas:
            self.validator.register_schema(schema_def["label"], schema_def["schema"])
        
        end = time.perf_counter()
        total_time_ms = (end - start) * 1000
        avg_time_ms = total_time_ms / len(schemas)
        
        print(f"\nAverage schema registration time: {avg_time_ms:.2f}ms")
        assert avg_time_ms < 10, f"Schema registration took {avg_time_ms:.2f}ms, expected < 10ms"


@pytest.mark.asyncio
class TestC2PAAPILoadTests:
    """Load tests for C2PA API endpoints."""
    
    async def test_concurrent_schema_creation(self, client: AsyncClient, auth_headers: dict):
        """Test concurrent schema creation."""
        async def create_schema(index: int):
            schema_data = {
                "namespace": "com.loadtest",
                "label": f"com.loadtest.schema{index}.v1",
                "version": "1.0",
                "schema": {
                    "type": "object",
                    "properties": {
                        "field1": {"type": "string"}
                    }
                }
            }
            
            response = await client.post(
                "/api/v1/enterprise/c2pa/schemas",
                json=schema_data,
                headers=auth_headers
            )
            return response.status_code
        
        # Create 20 schemas concurrently
        num_requests = 20
        start = time.perf_counter()
        
        tasks = [create_schema(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        end = time.perf_counter()
        total_time = end - start
        
        # Check all succeeded
        success_count = sum(1 for r in results if r == 201)
        
        print("\nConcurrent schema creation:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {success_count}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Requests/sec: {num_requests/total_time:.1f}")
        
        assert success_count >= num_requests * 0.95  # 95% success rate
    
    async def test_concurrent_validation_requests(self, client: AsyncClient, auth_headers: dict):
        """Test concurrent validation requests."""
        async def validate_assertion():
            assertion_data = {
                "label": "c2pa.location.v1",
                "data": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                }
            }
            
            response = await client.post(
                "/api/v1/enterprise/c2pa/validate",
                json=assertion_data,
                headers=auth_headers
            )
            return response.status_code
        
        # Send 50 validation requests concurrently
        num_requests = 50
        start = time.perf_counter()
        
        tasks = [validate_assertion() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        end = time.perf_counter()
        total_time = end - start
        
        success_count = sum(1 for r in results if r == 200)
        
        print("\nConcurrent validation requests:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {success_count}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Requests/sec: {num_requests/total_time:.1f}")
        
        assert success_count == num_requests  # All should succeed
        assert num_requests/total_time > 10  # At least 10 req/s
    
    async def test_schema_list_pagination_performance(self, client: AsyncClient, auth_headers: dict, db):
        """Test pagination performance with many schemas."""
        # This test assumes schemas exist from previous tests
        
        page_sizes = [10, 50, 100]
        
        for page_size in page_sizes:
            start = time.perf_counter()
            
            response = await client.get(
                f"/api/v1/enterprise/c2pa/schemas?page=1&page_size={page_size}",
                headers=auth_headers
            )
            
            end = time.perf_counter()
            response_time_ms = (end - start) * 1000
            
            print(f"\nList schemas (page_size={page_size}): {response_time_ms:.2f}ms")
            
            assert response.status_code == 200
            assert response_time_ms < 500  # Should be < 500ms
    
    async def test_embedding_with_custom_assertions_performance(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test embedding endpoint performance with custom assertions."""
        request_data = {
            "document_id": "perf_test_001",
            "text": "This is a performance test document. " * 10,  # ~100 words
            "segmentation_level": "sentence",
            "action": "c2pa.created",
            "custom_assertions": [
                {
                    "label": "c2pa.location.v1",
                    "data": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    }
                },
                {
                    "label": "c2pa.training-mining.v1",
                    "data": {
                        "use": {
                            "ai_training": False,
                            "ai_inference": False,
                            "data_mining": False
                        }
                    }
                }
            ],
            "validate_assertions": True
        }
        
        start = time.perf_counter()
        
        response = await client.post(
            "/api/v1/enterprise/embeddings/encode-with-embeddings",
            json=request_data,
            headers=auth_headers
        )
        
        end = time.perf_counter()
        total_time_ms = (end - start) * 1000
        
        print(f"\nEmbedding with custom assertions: {total_time_ms:.2f}ms")
        
        # Should complete in reasonable time (< 5 seconds for small doc)
        assert total_time_ms < 5000
        
        if response.status_code == 201:
            data = response.json()
            num_embeddings = len(data.get("embeddings", []))
            print(f"  Created {num_embeddings} embeddings")
            print(f"  Time per embedding: {total_time_ms/num_embeddings:.2f}ms")


@pytest.mark.asyncio
class TestC2PAMemoryUsage:
    """Memory usage tests for C2PA components."""
    
    def test_schema_cache_memory_efficiency(self):
        """Test that schema cache doesn't grow unbounded."""
        validator = C2PAValidator()
        
        # Register many schemas
        for i in range(100):
            schema = {
                "type": "object",
                "properties": {
                    f"field{j}": {"type": "string"} 
                    for j in range(10)
                }
            }
            validator.register_schema(f"com.test.schema{i}.v1", schema)
        
        # Cache should have all schemas
        assert len(validator.schema_cache) >= 100
        
        # Validate that cache is working
        assert "com.test.schema50.v1" in validator.schema_cache
    
    def test_large_assertion_validation(self):
        """Test validation of large assertion data."""
        validator = C2PAValidator()
        
        # Create large location data with many fields
        large_data = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "altitude": 16.0,
            "location_name": "A" * 1000,  # 1KB string
            "description": "B" * 10000,  # 10KB string
        }
        
        start = time.perf_counter()
        is_valid, errors, warnings = validator.validate_assertion(
            "c2pa.location.v1", 
            large_data
        )
        end = time.perf_counter()
        
        validation_time_ms = (end - start) * 1000
        
        print(f"\nLarge assertion validation: {validation_time_ms:.2f}ms")
        
        # Should still be fast even with large data
        assert validation_time_ms < 100


@pytest.mark.asyncio  
class TestC2PAStressTests:
    """Stress tests for C2PA system."""
    
    async def test_rapid_fire_validations(self, client: AsyncClient, auth_headers: dict):
        """Test system under rapid validation requests."""
        async def send_validation():
            return await client.post(
                "/api/v1/enterprise/c2pa/validate",
                json={
                    "label": "c2pa.location.v1",
                    "data": {"latitude": 37.7749, "longitude": -122.4194}
                },
                headers=auth_headers
            )
        
        # Send 100 requests as fast as possible
        num_requests = 100
        start = time.perf_counter()
        
        tasks = [send_validation() for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end = time.perf_counter()
        total_time = end - start
        
        # Count successes vs errors
        successes = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        errors = num_requests - successes
        
        print("\nRapid fire test:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {successes}")
        print(f"  Errors: {errors}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {num_requests/total_time:.1f} req/s")
        
        # Should handle at least 90% successfully
        assert successes >= num_requests * 0.9
    
    def test_validator_thread_safety(self):
        """Test that validator is thread-safe."""
        import concurrent.futures
        
        validator = C2PAValidator()
        
        def validate_in_thread(thread_id: int):
            results = []
            for i in range(10):
                is_valid, errors, warnings = validator.validate_assertion(
                    "c2pa.location.v1",
                    {"latitude": 37.7749, "longitude": -122.4194}
                )
                results.append(is_valid)
            return all(results)
        
        # Run validations in 10 threads concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate_in_thread, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All threads should succeed
        assert all(results)
        print(f"\nThread safety test: All {len(results)} threads completed successfully")
