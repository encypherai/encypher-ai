"""API endpoints for User Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
import httpx

from ...db.session import get_db
from ...models.schemas import ProfileUpdate, ProfileResponse, TeamCreate, TeamResponse
from ...services.user_service import UserService
from ...core.config import settings

router = APIRouter()


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service unavailable")


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get user profile"""
    profile = UserService.get_or_create_profile(db, current_user["id"])
    return profile


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update user profile"""
    profile = UserService.update_profile(db, current_user["id"], profile_data)
    return profile


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a team"""
    team = UserService.create_team(db, current_user["id"], team_data)
    return team


@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get user teams"""
    teams = UserService.get_user_teams(db, current_user["id"])
    return teams


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user-service"}
