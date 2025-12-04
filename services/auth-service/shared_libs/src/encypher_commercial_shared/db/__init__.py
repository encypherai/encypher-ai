"""
Database utilities for Encypher microservices.

This module provides shared database functionality including:
- Connection validation
- Automatic migration running
- Health checks
"""

from .startup import (
    check_database_connection,
    run_migrations_if_needed,
    ensure_database_ready,
    DatabaseStartupError,
)

__all__ = [
    "check_database_connection",
    "run_migrations_if_needed", 
    "ensure_database_ready",
    "DatabaseStartupError",
]
