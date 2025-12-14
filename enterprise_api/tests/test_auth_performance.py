import os

# Set required env vars before importing app
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
os.environ["KEY_ENCRYPTION_KEY"] = "00" * 32
os.environ["ENCRYPTION_NONCE"] = "00" * 12
os.environ["SSL_COM_API_KEY"] = "test_key"

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app import dependencies
from app.dependencies import get_current_organization


@pytest.mark.asyncio
async def test_get_current_organization_uses_client():
    """
    Test that dependency uses KeyServiceClient and not direct DB calls.
    """
    
    with patch.object(dependencies, "key_service_client") as mock_service_client:
        mock_service_client.validate_key = AsyncMock(return_value={
            "api_key": "test_key",
            "organization_id": "org_1",
            "tier": "professional",
            "api_calls_this_month": 0,
            "monthly_quota": 1000
        })
        
        # Mock credentials
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test_key"

        # Mock BackgroundTasks
        mock_background_tasks = MagicMock()

        # Mock Request with .state for metrics fields
        mock_request = MagicMock()
        mock_request.state = MagicMock()

        # Call the dependency (no DB arg needed now)
        result = await get_current_organization(
            request=mock_request,
            background_tasks=mock_background_tasks,
            credentials=mock_credentials
        )

        # Verify client was called
        mock_service_client.validate_key.assert_called_once_with("test_key")
        
        # Verify result matches
        assert result["organization_id"] == "org_1"
