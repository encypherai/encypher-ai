"""API endpoints for Notification Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
import httpx

from ...db.session import get_db
from ...models.schemas import NotificationCreate, NotificationResponse
from ...services.notification_service import NotificationService
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


@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Send a notification"""
    notification = NotificationService.create_notification(db, current_user["id"], notification_data)
    return notification


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get user notifications"""
    notifications = NotificationService.get_user_notifications(db, current_user["id"], limit)
    return notifications


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notification-service"}
