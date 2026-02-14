"""
Onboarding Checklist Service

TEAM_191: Server-side onboarding checklist tracked per user.
Replaces the old localStorage-based onboarding modal with real
milestone tracking stored in the database.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import User
from app.models.schemas import OnboardingStatusResponse, OnboardingStepStatus

logger = logging.getLogger(__name__)

# Canonical onboarding steps — order matters for display
ONBOARDING_STEPS = [
    {
        "step_id": "account_created",
        "title": "Create your account",
        "description": "Sign up for Encypher and get instant API access.",
        "action_url": None,
    },
    {
        "step_id": "publisher_identity_set",
        "title": "Set up your publisher identity",
        "description": "Choose how your name appears on signed content.",
        "action_url": None,  # Handled by the mandatory setup wizard
    },
    {
        "step_id": "first_api_key",
        "title": "Generate your first API key",
        "description": "Create an API key to start signing and verifying content.",
        "action_url": "/api-keys",
    },
    {
        "step_id": "first_api_call",
        "title": "Make your first API call",
        "description": "Use your API key to call the Encypher API.",
        "action_url": "/docs/publisher-integration",
    },
    {
        "step_id": "first_document_signed",
        "title": "Sign your first document",
        "description": "Authenticate content with a cryptographic signature.",
        "action_url": "/playground",
    },
    {
        "step_id": "first_verification",
        "title": "Verify a signed document",
        "description": "Confirm the authenticity of signed content.",
        "action_url": "/playground",
    },
]

VALID_STEP_IDS = {step["step_id"] for step in ONBOARDING_STEPS}


class OnboardingService:
    """
    Service for managing per-user onboarding checklists.

    The checklist is stored as a JSON dict on the User model:
    {
        "account_created": {"completed_at": "2026-02-14T12:00:00Z"},
        "first_api_key": {"completed_at": "2026-02-14T12:05:00Z"},
        ...
        "_dismissed": true  // optional flag
    }
    """

    def __init__(self, db: Session):
        self.db = db

    def get_onboarding_status(self, user_id: str) -> OnboardingStatusResponse:
        """Get the full onboarding checklist status for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        checklist: Dict = user.onboarding_checklist or {}
        dismissed = checklist.get("_dismissed", False)

        steps: List[OnboardingStepStatus] = []
        completed_count = 0

        for step_def in ONBOARDING_STEPS:
            step_data = checklist.get(step_def["step_id"], {})
            completed = bool(step_data.get("completed_at"))
            completed_at_str = step_data.get("completed_at")
            completed_at = None
            if completed_at_str:
                try:
                    completed_at = datetime.fromisoformat(completed_at_str)
                except (ValueError, TypeError):
                    completed_at = None

            if completed:
                completed_count += 1

            steps.append(
                OnboardingStepStatus(
                    step_id=step_def["step_id"],
                    title=step_def["title"],
                    description=step_def["description"],
                    completed=completed,
                    completed_at=completed_at,
                    action_url=step_def["action_url"],
                )
            )

        total_count = len(ONBOARDING_STEPS)
        all_completed = completed_count == total_count

        return OnboardingStatusResponse(
            steps=steps,
            completed_count=completed_count,
            total_count=total_count,
            all_completed=all_completed,
            dismissed=dismissed,
            completed_at=user.onboarding_completed_at,
        )

    def complete_step(self, user_id: str, step_id: str) -> OnboardingStatusResponse:
        """Mark an onboarding step as complete."""
        if step_id not in VALID_STEP_IDS:
            raise ValueError(f"Invalid onboarding step: {step_id}")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        checklist: Dict = dict(user.onboarding_checklist or {})

        # Only set if not already completed (idempotent)
        if not checklist.get(step_id, {}).get("completed_at"):
            checklist[step_id] = {
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            user.onboarding_checklist = checklist

            # Check if all steps are now complete
            completed_steps = sum(
                1 for s in ONBOARDING_STEPS
                if checklist.get(s["step_id"], {}).get("completed_at")
            )
            if completed_steps == len(ONBOARDING_STEPS) and not user.onboarding_completed_at:
                user.onboarding_completed_at = datetime.now(timezone.utc)

            self.db.commit()
            logger.info(f"TEAM_191: User {user_id} completed onboarding step: {step_id}")

        return self.get_onboarding_status(user_id)

    def dismiss_checklist(self, user_id: str) -> OnboardingStatusResponse:
        """Dismiss the onboarding checklist (user chose to hide it)."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        checklist: Dict = dict(user.onboarding_checklist or {})
        checklist["_dismissed"] = True
        user.onboarding_checklist = checklist
        self.db.commit()

        logger.info(f"TEAM_191: User {user_id} dismissed onboarding checklist")
        return self.get_onboarding_status(user_id)

    def initialize_for_new_user(self, user_id: str) -> None:
        """Initialize onboarding for a newly created user (mark account_created)."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        checklist: Dict = dict(user.onboarding_checklist or {})
        if not checklist.get("account_created", {}).get("completed_at"):
            checklist["account_created"] = {
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            user.onboarding_checklist = checklist
            # Don't commit here — caller manages the transaction
            logger.info(f"TEAM_191: Initialized onboarding for new user {user_id}")
