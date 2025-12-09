"""
API endpoints for CLI tool integration.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.services.cli_integration import run_scheduled_scan
from app.services.user import get_current_active_superuser

router = APIRouter()

@router.post("/scan", status_code=status.HTTP_202_ACCEPTED)
async def run_scan(
    background_tasks: BackgroundTasks,
    input_path: str,
    policy_file: Optional[str] = None,
    db: AsyncSession = Depends(get_db), # db session from request, primarily for current_user or initial checks
    current_user: User = Depends(get_current_active_superuser)
) -> Dict[str, Any]:
    """
    Run a scan using the CLI tools in the background.
    Only superusers can trigger scans.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to file or directory to scan
        policy_file: Optional path to policy file
        db: Database session
        current_user: Current authenticated superuser
        
    Returns:
        Dictionary with scan status
    """
    # Add the scan to background tasks
    background_tasks.add_task(
        run_scheduled_scan, # run_scheduled_scan will create its own session
        input_path=input_path,
        policy_file=policy_file
    )
    
    return {
        "message": "Scan started in the background",
        "input_path": input_path,
        "policy_file": policy_file,
        "triggered_by": current_user.username
    }
