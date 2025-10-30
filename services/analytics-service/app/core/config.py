"""Configuration management for Analytics Service"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    SERVICE_NAME: str = "analytics-service"
    SERVICE_PORT: int = 8006
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    REDIS_URL: str = "redis://localhost:6379/4"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 4
    
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    API_GATEWAY_URL: str = "http://localhost:8000"
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    PROMETHEUS_PORT: int = 9006
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
