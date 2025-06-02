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
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./encypherai_dashboard.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # FastAPI backend
        "http://localhost",
    ]

settings = Settings()
