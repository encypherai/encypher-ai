import os

from app.api.api import api_router
from app.core.config import settings
from app.core.database import Base, engine
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
# Base.metadata.create_all(bind=engine) # Replaced by async creation in startup_tasks

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB tables and initial superuser
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")

    from app.core.database import AsyncSessionLocal
    from app.services.user import create_user, get_user_by_email

    admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")

    if admin_email and admin_password:
        async with AsyncSessionLocal() as db:
            try:
                user = await get_user_by_email(db=db, email=admin_email)
                if not user:
                    await create_user(
                        db=db,
                        username="admin",
                        email=admin_email,
                        password=admin_password,
                        full_name="System Administrator",
                        is_superuser=True,
                    )
                    print(f"Attempted to create initial admin user: {admin_email}")
            except Exception as e:
                print(f"Error during initial admin user creation: {e}")
    yield
    # Shutdown: Any cleanup tasks would go here (e.g., closing DB connections if not handled by context managers)
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
