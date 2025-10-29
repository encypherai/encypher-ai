import os
import asyncio
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file BEFORE importing settings
load_dotenv()

from app.api.api import api_router
from app.core.config import settings
from app.core.database import Base, engine, AsyncSessionLocal
from app.services.user import create_user, get_user_by_email, get_user_by_username
from app.utils.caching import cleanup_expired_cache_entries

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB tables and initial superuser
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")

    # Start cache cleanup task
    cache_cleanup_task = asyncio.create_task(cleanup_expired_cache_entries())
    logging.info("Started cache cleanup background task")

    admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")

    if admin_email and admin_password:
        async with AsyncSessionLocal() as db:
            try:
                # Check if user exists by email or username
                user_by_email = await get_user_by_email(db=db, email=admin_email)
                user_by_username = await get_user_by_username(db=db, username="admin")
                
                if not user_by_email and not user_by_username:
                    await create_user(
                        db=db,
                        username="admin",
                        email=admin_email,
                        password=admin_password,
                        full_name="System Administrator",
                        is_superuser=True,
                    )
                    print(f"Created initial admin user: {admin_email}")
                else:
                    print(f"Initial admin user already exists, skipping creation")
            except Exception as e:
                print(f"Error during initial admin user creation: {e}")
    yield
    # Shutdown: Any cleanup tasks would go here (e.g., closing DB connections if not handled by context managers)
    cache_cleanup_task.cancel()
    try:
        await cache_cleanup_task
    except asyncio.CancelledError:
        logging.info("Cache cleanup task cancelled")
    except Exception as e:
        logging.error(f"Error cancelling cache cleanup task: {e}")
    print("Application shutdown.")

app = FastAPI(
    title="EncypherAI Dashboard Backend",
    version="0.1.0",
    description="API for the EncypherAI Compliance Readiness Dashboard",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the EncypherAI Dashboard Backend"}


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
