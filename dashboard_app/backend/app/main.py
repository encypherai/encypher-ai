from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="EncypherAI Dashboard Backend",
    version="0.1.0",
    description="API for the EncypherAI Compliance Readiness Dashboard"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the EncypherAI Dashboard Backend"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

# Placeholder for other routers
# from .api import items_router, users_router # Example
# app.include_router(items_router, prefix="/api/v1")
# app.include_router(users_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
