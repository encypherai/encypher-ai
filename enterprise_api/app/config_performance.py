"""
Performance configuration for database operations.

This module provides configuration options for optimizing database performance,
particularly for high-throughput write workloads.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class PerformanceSettings(BaseSettings):
    """
    Performance tuning settings for the Enterprise API.
    
    These settings control database commit behavior and can dramatically
    improve performance for write-heavy workloads.
    """
    
    # Database commit batching
    DB_BATCH_COMMITS: bool = True
    """Enable batch commits to reduce disk fsync() operations"""
    
    DB_BATCH_SIZE: int = 100
    """Number of operations before forcing a commit (default: 100)"""
    
    DB_BATCH_TIMEOUT: float = 1.0
    """Maximum seconds to wait before forcing a commit (default: 1.0)"""
    
    # Database connection pool (already in database.py, documented here)
    DB_POOL_SIZE: int = 100
    """Number of database connections in the pool (default: 100)"""
    
    DB_MAX_OVERFLOW: int = 50
    """Additional connections allowed beyond pool_size (default: 50)"""
    
    # Write optimization
    DB_USE_FLUSH_INSTEAD_OF_COMMIT: bool = True
    """
    Use flush() instead of commit() for individual operations.
    The session will auto-commit at the end of the request.
    This is the simplest and most effective optimization.
    """
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global performance settings instance
perf_settings = PerformanceSettings()
