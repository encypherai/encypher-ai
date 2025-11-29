"""
Pytest configuration for auth-service tests
"""
import sys
from pathlib import Path

# Add the auth-service root to the path so we can import app modules
auth_service_root = Path(__file__).parent.parent
sys.path.insert(0, str(auth_service_root))

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)
