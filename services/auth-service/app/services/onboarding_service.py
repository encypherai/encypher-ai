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

from app.db.models import Organization, User
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

    def _get_organization(self, user: User) -> Optional[Organization]:
        if not user.default_organization_id:
            return None
        return self.db.query(Organization).filter(Organization.id == user.default_organization_id).first()

    def _tailor_step_definition(self, step_def: Dict, user: User, org: Optional[Organization]) -> Dict:
        tailored = dict(step_def)

        workflow = None
        if org:
            workflow = org.workflow_category or ("media_publishing" if org.dashboard_layout == "publisher" else "enterprise")

        platform = org.publisher_platform if org else None
        publisher_name_label = "your name" if user.default_organization_id and org and org.account_type == "individual" else "your publisher identity"

        if step_def["step_id"] == "publisher_identity_set":
            if workflow == "media_publishing":
                tailored["title"] = "Set up your publisher identity"
                tailored["description"] = f"Choose how {publisher_name_label} appears on signed content."
            elif workflow == "ai_provenance_governance":
                tailored["title"] = "Set up your governance workspace"
                tailored["description"] = "Choose the team or operator identity for attested AI workflows."
            else:
                tailored["title"] = "Set up your workspace identity"
                tailored["description"] = "Choose how your team appears across implementation and rollout surfaces."

        if step_def["step_id"] == "first_api_key":
            if workflow == "media_publishing":
                tailored["title"] = "Generate your publisher API key"
                tailored["description"] = "Create credentials for your CMS integration or publishing workflow."
            elif workflow == "ai_provenance_governance":
                tailored["title"] = "Generate governance credentials"
                tailored["description"] = "Create the credentials needed for attested AI workflow integrations."
            else:
                tailored["title"] = "Generate implementation credentials"
                tailored["description"] = "Create the credentials your team needs to stand up the integration."

        if step_def["step_id"] == "first_api_call":
            if workflow == "media_publishing":
                if platform == "wordpress":
                    tailored["title"] = "Install the WordPress plugin"
                    tailored["description"] = "Connect WordPress and start signing published content quickly."
                    tailored["action_url"] = "/docs/wordpress-integration"
                elif platform == "ghost":
                    tailored["title"] = "Connect your Ghost site"
                    tailored["description"] = "Open the Ghost integration path and prepare your first signed post."
                    tailored["action_url"] = "/integrations"
                elif platform == "substack":
                    tailored["title"] = "Open the Substack guide"
                    tailored["description"] = "Follow the fastest path for signed newsletter provenance."
                    tailored["action_url"] = "/docs/publisher-integration"
                elif platform in {"custom", "custom_cms", "other"}:
                    tailored["title"] = "Review your CMS integration guide"
                    tailored["description"] = "Follow the implementation guide for your publishing stack."
                    tailored["action_url"] = "/docs/publisher-integration"
                else:
                    tailored["title"] = "Open the publisher integration guide"
                    tailored["description"] = "Start with the fastest path to get signed publishing live."
                    tailored["action_url"] = "/docs/publisher-integration"
            elif workflow == "ai_provenance_governance":
                tailored["title"] = "Open the AI governance guide"
                tailored["description"] = "Review the guided path for attested records, controls, and rollout."
                tailored["action_url"] = "/docs"
            else:
                tailored["title"] = "Open the implementation guide"
                tailored["description"] = "Review the fastest path to stand up and validate your enterprise workflow."
                tailored["action_url"] = "/docs"

        if step_def["step_id"] == "first_document_signed":
            if workflow == "media_publishing":
                tailored["title"] = "Sign your first article"
                tailored["description"] = "Create proof of origin that survives downstream distribution."
            elif workflow == "ai_provenance_governance":
                tailored["title"] = "Create your first attested record"
                tailored["description"] = "Generate a governed, cryptographically attested AI output."
            else:
                tailored["title"] = "Run your first signing workflow"
                tailored["description"] = "Validate the happy path before rolling the integration out further."

        if step_def["step_id"] == "first_verification":
            if workflow == "media_publishing":
                tailored["title"] = "Verify publisher provenance"
                tailored["description"] = "Confirm signed content verifies the way readers and partners will see it."
            elif workflow == "ai_provenance_governance":
                tailored["title"] = "Verify and document evidence"
                tailored["description"] = "Confirm the attested record is verification-ready for review and audit."
            else:
                tailored["title"] = "Verify signed output"
                tailored["description"] = "Confirm trust signals before broader team rollout."

        return tailored

    def get_onboarding_status(self, user_id: str) -> OnboardingStatusResponse:
        """Get the full onboarding checklist status for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        checklist: Dict = user.onboarding_checklist or {}
        dismissed = checklist.get("_dismissed", False)
        org = self._get_organization(user)

        steps: List[OnboardingStepStatus] = []
        completed_count = 0

        for step_def in ONBOARDING_STEPS:
            tailored_step_def = self._tailor_step_definition(step_def, user, org)
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
                    step_id=tailored_step_def["step_id"],
                    title=tailored_step_def["title"],
                    description=tailored_step_def["description"],
                    completed=completed,
                    completed_at=completed_at,
                    action_url=tailored_step_def["action_url"],
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
            completed_steps = sum(1 for s in ONBOARDING_STEPS if checklist.get(s["step_id"], {}).get("completed_at"))
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
