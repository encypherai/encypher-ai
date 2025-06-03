"""
Configuration settings for the EncypherAI Dashboard Backend.
"""
import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    """Application settings."""
    PROJECT_NAME: str = "EncypherAI Dashboard"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Frontend URL for links in emails
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./encypherai_dashboard.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # FastAPI backend
        "http://localhost",
    ]
    
    # Email settings
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@encypherai.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "EncypherAI Dashboard")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "25"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "False").lower() == "true"

settings = Settings()
