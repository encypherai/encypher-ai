import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import os

# Set env vars
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
os.environ["KEY_ENCRYPTION_KEY"] = "00" * 32
os.environ["ENCRYPTION_NONCE"] = "00" * 12
os.environ["SSL_COM_API_KEY"] = "test_key"

from app.services.key_service_client import KeyServiceClient

@pytest.mark.asyncio
async def test_validate_key_uses_cache():
    """Test that validate_key uses Redis cache if available."""
    
    mock_redis = AsyncMock()
    # Mock Redis get to return cached key info
    mock_redis.get.return_value = '{"api_key": "test_key", "organization_id": "org_1", "can_sign": true}'
    
    service = KeyServiceClient(redis_client=mock_redis)
    
    # Mock http client
    with patch("httpx.AsyncClient") as mock_client:
        result = await service.validate_key("test_key")
        
        # Should return cached result
        assert result["organization_id"] == "org_1"
        assert result["can_sign"] is True
        
        # Should NOT call HTTP service
        mock_client.return_value.__aenter__.return_value.post.assert_not_called()

@pytest.mark.asyncio
async def test_validate_key_calls_service_on_cache_miss():
    """Test that validate_key calls service on cache miss and sets cache."""
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    
    service = KeyServiceClient(redis_client=mock_redis)
    
    # Mock http response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "valid": True,
        "key": {
            "api_key": "test_key",
            "organization_id": "org_service",
            "can_sign": True
        }
    }
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
        
        result = await service.validate_key("test_key")
        
        # Should return service result
        assert result["organization_id"] == "org_service"
        
        # Should call HTTP service
        mock_client_instance.post.assert_called_once()
        
        # Should cache result
        mock_redis.setex.assert_called_once()
