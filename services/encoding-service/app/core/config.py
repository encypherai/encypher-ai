"""
Configuration management for Encoding Service

Environment Variables:
- Shared: CONTENT_DATABASE_URL, REDIS_URL, ALLOWED_ORIGINS, AUTH_SERVICE_URL, KEY_SERVICE_URL
- Service-specific: DEFAULT_ENCODING, MAX_DOCUMENT_SIZE, SUPPORTED_FORMATS
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "encoding-service"
    SERVICE_PORT: int = 8004
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    # ===========================================
    # SHARED: Database (from shared vars)
    # Note: Encoding service uses CONTENT database
    # ===========================================
    DATABASE_URL: str  # Points to content DB
    CONTENT_DATABASE_URL: str = ""  # Alias, falls back to DATABASE_URL
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # ===========================================
    # SHARED: Redis (from shared vars)
    # ===========================================
    REDIS_URL: str = "redis://localhost:6379"
    
    # ===========================================
    # SHARED: CORS (from shared vars)
    # ===========================================
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # ===========================================
    # SHARED: Internal Service URLs (from shared vars)
    # ===========================================
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    KEY_SERVICE_URL: str = "http://localhost:8003"
    
    # ===========================================
    # SERVICE-SPECIFIC: Encoding Configuration
    # ===========================================
    DEFAULT_ENCODING: str = "unicode"
    MAX_DOCUMENT_SIZE: int = 10485760  # 10MB
    SUPPORTED_FORMATS: str = "text,json,markdown"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def supported_formats_list(self) -> List[str]:
        """Parse SUPPORTED_FORMATS into a list"""
        return [fmt.strip() for fmt in self.SUPPORTED_FORMATS.split(",")]
    
    @property
    def db_url(self) -> str:
        """Get the appropriate database URL"""
        return self.CONTENT_DATABASE_URL or self.DATABASE_URL


# Global settings instance
settings = Settings()
