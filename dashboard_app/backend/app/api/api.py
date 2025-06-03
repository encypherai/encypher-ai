"""
API router for the EncypherAI Dashboard Backend.
"""
from fastapi import APIRouter

from app.api.endpoints import auth, audit_logs, policy_validation, cli, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit logs"])
api_router.include_router(policy_validation.router, prefix="/policy-validation", tags=["policy validation"])
api_router.include_router(cli.router, prefix="/cli", tags=["cli integration"])
