"""API endpoints for User Service v1"""

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db.session import get_db
from ...models.schemas import (
    PaginatedResponse,
    ProfileResponse,
    ProfileUpdate,
    TeamCreate,
    TeamResponse,
)
from ...services.user_service import UserService

router = APIRouter()


async def get_current_user(request: Request, authorization: str = Header(...)) -> dict:
    """Verify user token with the auth service using the shared HTTP client.

    Expects Authorization header in the form: 'Bearer <token>'
    """
    client: httpx.AsyncClient = request.app.state.http_client
    try:
        response = await client.post(
            f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
            headers={"Authorization": authorization},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Invalid credentials",
                    "hint": (
                        "Supply a valid Bearer token in the Authorization header: "
                        "Authorization: Bearer <your-token>. "
                        "Obtain a token via POST /api/v1/auth/login."
                    ),
                },
            )
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": f"Auth service unavailable: {e}",
                "hint": ("The authentication service is temporarily unreachable. Retry after a short delay. Check service health at GET /health."),
            },
        ) from e


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the authenticated user's profile.

    Returns the profile record for the caller identified by the Bearer token.
    If no profile exists yet, one is created automatically.
    """
    profile = UserService.get_or_create_profile(db, current_user["id"])
    return profile


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update the authenticated user's profile.

    All fields are optional; only supplied fields are written.
    Example body: {"display_name": "Alice", "bio": "Engineer at Acme"}
    """
    profile = UserService.update_profile(db, current_user["id"], profile_data)
    return profile


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new team owned by the authenticated user.

    Required fields: name (string).
    Optional fields: description (string).
    Example body: {"name": "Acme Docs", "description": "Document team"}
    """
    team = UserService.create_team(db, current_user["id"], team_data)
    return team


@router.get("/teams", response_model=PaginatedResponse[TeamResponse])
async def get_teams(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
):
    """List teams owned by or shared with the authenticated user.

    Results are paginated. Use 'page' and 'page_size' query params to navigate.
    Example: GET /api/v1/users/teams?page=1&page_size=50
    """
    all_teams = UserService.get_user_teams(db, current_user["id"])
    total = len(all_teams)
    offset = (page - 1) * page_size
    page_items = all_teams[offset : offset + page_size]
    next_page = page + 1 if offset + page_size < total else None
    return PaginatedResponse(
        items=page_items,
        total=total,
        page=page,
        page_size=page_size,
        next_page=next_page,
    )
