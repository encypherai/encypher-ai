"""
Configuration management for Coalition Service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Service Configuration
    SERVICE_NAME: str = "coalition-service"
    SERVICE_PORT: int = 8009
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/2"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 2

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # API Gateway
    API_GATEWAY_URL: str = "http://localhost:8000"

    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ENTERPRISE_API_URL: str = "http://localhost:8002"

    # Coalition Settings
    REVENUE_SPLIT_ENCYPHER: int = 30
    REVENUE_SPLIT_MEMBERS: int = 70
    MIN_PAYOUT_THRESHOLD: float = 10.0
    AUTO_ONBOARD_FREE_TIER: bool = True

    # Service Discovery
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500

    # Monitoring
    PROMETHEUS_PORT: int = 9009

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
