"""Configuration management for Notification Service"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8008
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/6"
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Email Configuration (uses shared email library)
    SMTP_HOST: str = "smtp.zoho.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""  # Renamed from SMTP_PASSWORD for consistency
    SMTP_TLS: bool = True
    EMAIL_FROM: str = "support@encypherai.com"
    EMAIL_FROM_NAME: str = "Support - Encypher"
    FRONTEND_URL: str = "http://localhost:3000"
    DASHBOARD_URL: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
