"""
Configuration management for Encoding Service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    SERVICE_NAME: str = "encoding-service"
    SERVICE_PORT: int = 8004
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
    
    # Auth Service
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    
    # Key Service
    KEY_SERVICE_URL: str = "http://localhost:8003"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # API Gateway
    API_GATEWAY_URL: str = "http://localhost:8000"
    
    # Service Discovery
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    
    # Monitoring
    PROMETHEUS_PORT: int = 9004
    
    # Encoding Configuration
    DEFAULT_ENCODING: str = "unicode"
    MAX_DOCUMENT_SIZE: int = 10485760  # 10MB
    SUPPORTED_FORMATS: str = "text,json,markdown"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def supported_formats_list(self) -> List[str]:
        """Parse SUPPORTED_FORMATS into a list"""
        return [fmt.strip() for fmt in self.SUPPORTED_FORMATS.split(",")]


# Global settings instance
settings = Settings()
