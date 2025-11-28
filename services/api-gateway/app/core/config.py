"""
Configuration for API Gateway

Environment Variables:
- Shared: REDIS_URL, ALLOWED_ORIGINS, AUTH_SERVICE_URL
- Service-specific: PROXY_* timeouts, downstream service URLs
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
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
    BILLING_SERVICE_URL: str = "http://localhost:8007"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8006"
    
    # ===========================================
    # SERVICE-SPECIFIC: Downstream Services
    # ===========================================
    ENTERPRISE_API_URL: str = "http://localhost:9000"
    
    # ===========================================
    # SERVICE-SPECIFIC: Proxy Configuration
    # ===========================================
    PROXY_CONNECT_TIMEOUT: int = 5
    PROXY_READ_TIMEOUT: int = 30
    PROXY_WRITE_TIMEOUT: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
