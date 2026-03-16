"""
API Access Gating Service

TEAM_006: Handles user API access requests and admin approval workflow.

Industry best practice: Users must request and be approved for API access
before they can generate API keys. This enables controlled rollout and
quality early adopters during preview/beta phases.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import inspect, literal, select
from sqlalchemy.orm import Session

from app.db.models import User, ApiAccessStatus
from app.models.schemas import (
    ApiAccessStatusResponse,
    PendingAccessRequest,
    ApiAccessStatus as ApiAccessStatusEnum,
)

# Email imports
try:
    from encypher_commercial_shared.email import (
        EmailConfig,
        send_api_access_approved_email,
        send_api_access_denied_email,
        send_api_access_request_admin_email,
    )

    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

logger = logging.getLogger(__name__)


def _get_email_config() -> "EmailConfig":
    """Create email config from settings. Import lazily to avoid test issues."""
    from app.core.auth import get_email_config

    return get_email_config()


class ApiAccessService:
    """
    Service for managing API access requests and approvals.

    Flow:
    1. User signs up (default: NOT_REQUESTED)
    2. User requests API access with use case description
    3. Admin reviews and approves/denies
    4. Approved users can generate API keys
    """

    def __init__(self, db: Session):
        self.db = db

    def _table_columns(self, table_name: str) -> set[str]:
        return {column["name"] for column in inspect(self.db.get_bind()).get_columns(table_name)}

    async def get_api_access_status(self, user_id: str) -> ApiAccessStatusResponse:
        """
        Get the current API access status for a user.

        Args:
            user_id: The user's ID

        Returns:
            ApiAccessStatusResponse with current status and details

        Raises:
            ValueError: If user not found
        """
        query_failed = False
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
        except Exception:
            query_failed = True
            user = None

        if not query_failed:
            if not user:
                raise ValueError("User not found")

            status = ApiAccessStatusEnum(user.api_access_status)

            messages = {
                ApiAccessStatusEnum.NOT_REQUESTED: "You have not requested API access yet.",
                ApiAccessStatusEnum.PENDING: "Your API access request is pending review.",
                ApiAccessStatusEnum.APPROVED: "Your API access has been approved. You can now generate API keys.",
                ApiAccessStatusEnum.DENIED: "Your API access request was denied. You may submit a new request with more details.",
                ApiAccessStatusEnum.SUSPENDED: (
                    "Your API access has been suspended. If you believe this is an error, please contact support at support@encypherai.com."
                ),
            }

            return ApiAccessStatusResponse(
                status=status,
                requested_at=user.api_access_requested_at,
                decided_at=user.api_access_decided_at,
                use_case=user.api_access_use_case,
                denial_reason=user.api_access_denial_reason,
                message=messages.get(status),
            )

        user_columns = self._table_columns(User.__tablename__)
        user_query = select(
            User.id.label("id"),
            (User.api_access_status if "api_access_status" in user_columns else literal(ApiAccessStatusEnum.APPROVED.value)).label(
                "api_access_status"
            ),
            (User.api_access_requested_at if "api_access_requested_at" in user_columns else literal(None)).label("api_access_requested_at"),
            (User.api_access_decided_at if "api_access_decided_at" in user_columns else literal(None)).label("api_access_decided_at"),
            (User.api_access_use_case if "api_access_use_case" in user_columns else literal(None)).label("api_access_use_case"),
            (User.api_access_denial_reason if "api_access_denial_reason" in user_columns else literal(None)).label("api_access_denial_reason"),
        ).where(User.id == user_id)
        user_row = self.db.execute(user_query).mappings().first()

        if not user_row:
            raise ValueError("User not found")

        status = ApiAccessStatusEnum(user_row["api_access_status"] or ApiAccessStatusEnum.APPROVED.value)

        messages = {
            ApiAccessStatusEnum.NOT_REQUESTED: "You have not requested API access yet.",
            ApiAccessStatusEnum.PENDING: "Your API access request is pending review.",
            ApiAccessStatusEnum.APPROVED: "Your API access has been approved. You can now generate API keys.",
            ApiAccessStatusEnum.DENIED: "Your API access request was denied. You may submit a new request with more details.",
            ApiAccessStatusEnum.SUSPENDED: (
                "Your API access has been suspended. If you believe this is an error, please contact support at support@encypherai.com."
            ),
        }

        return ApiAccessStatusResponse(
            status=status,
            requested_at=user_row["api_access_requested_at"],
            decided_at=user_row["api_access_decided_at"],
            use_case=user_row["api_access_use_case"],
            denial_reason=user_row["api_access_denial_reason"],
            message=messages.get(status),
        )

    async def list_pending_requests(self) -> List[PendingAccessRequest]:
        """
        List all pending API access requests for admin review.

        Returns:
            List of PendingAccessRequest objects, ordered by request date
        """
        query_failed = False
        try:
            pending_users = (
                self.db.query(User).filter(User.api_access_status == ApiAccessStatus.PENDING.value).order_by(User.api_access_requested_at.asc()).all()
            )
        except Exception:
            query_failed = True
            pending_users = []

        if not query_failed:
            return [
                PendingAccessRequest(
                    user_id=user.id,
                    email=user.email,
                    name=user.name,
                    use_case=user.api_access_use_case or "",
                    requested_at=user.api_access_requested_at or datetime.now(timezone.utc),
                )
                for user in pending_users
            ]

        user_columns = self._table_columns(User.__tablename__)
        required_columns = {"id", "email", "name", "api_access_status"}
        if not required_columns.issubset(user_columns):
            return []

        query = select(
            User.id.label("id"),
            User.email.label("email"),
            User.name.label("name"),
            (User.api_access_use_case if "api_access_use_case" in user_columns else literal(None)).label("api_access_use_case"),
            (User.api_access_requested_at if "api_access_requested_at" in user_columns else literal(None)).label("api_access_requested_at"),
        ).where(User.api_access_status == ApiAccessStatus.PENDING.value)
        if "api_access_requested_at" in user_columns:
            query = query.order_by(User.api_access_requested_at.asc())

        rows = self.db.execute(query).mappings().all()

        return [
            PendingAccessRequest(
                user_id=row["id"],
                email=row["email"],
                name=row["name"],
                use_case=row["api_access_use_case"] or "",
                requested_at=row["api_access_requested_at"] or datetime.now(timezone.utc),
            )
            for row in rows
        ]

    async def is_api_access_approved(self, user_id: str) -> bool:
        """
        Quick check if a user has approved API access.

        Used by key-service to gate API key generation.

        Args:
            user_id: The user's ID

        Returns:
            True if approved, False otherwise
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        return user.api_access_status == ApiAccessStatus.APPROVED.value

    async def set_api_access_status(self, user_id: str, new_status: str, admin_user_id: str, reason: Optional[str] = None) -> ApiAccessStatusResponse:
        """
        TEAM_164: Admin directly sets a user's API access status.

        Allows admins to set any status: not_requested, pending, approved, denied, suspended.
        This bypasses the normal request/approve flow for admin overrides.

        Args:
            user_id: The user to update
            new_status: The new API access status value
            admin_user_id: The admin making the change
            reason: Optional reason for the change

        Returns:
            ApiAccessStatusResponse with the new status

        Raises:
            ValueError: If user not found or invalid status
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        try:
            status_enum = ApiAccessStatus(new_status)
        except ValueError:
            valid = [s.value for s in ApiAccessStatus]
            raise ValueError(f"Invalid API access status: {new_status}. Must be one of: {valid}")

        previous_status = user.api_access_status
        user.api_access_status = status_enum.value
        user.api_access_decided_at = datetime.now(timezone.utc)
        user.api_access_decided_by = admin_user_id

        if new_status == ApiAccessStatus.SUSPENDED.value:
            user.api_access_denial_reason = reason or "API access suspended by administrator"
        elif new_status == ApiAccessStatus.DENIED.value:
            user.api_access_denial_reason = reason
        elif new_status in (ApiAccessStatus.APPROVED.value, ApiAccessStatus.NOT_REQUESTED.value):
            user.api_access_denial_reason = None

        self.db.commit()

        logger.info(f"TEAM_164: Admin {admin_user_id} set API access status for user {user_id}: {previous_status} -> {new_status} (reason: {reason})")

        messages = {
            ApiAccessStatusEnum.NOT_REQUESTED: "API access status reset.",
            ApiAccessStatusEnum.PENDING: "API access status set to pending.",
            ApiAccessStatusEnum.APPROVED: "API access has been approved.",
            ApiAccessStatusEnum.DENIED: "API access has been denied.",
            ApiAccessStatusEnum.SUSPENDED: "API access has been suspended.",
        }

        return ApiAccessStatusResponse(
            status=ApiAccessStatusEnum(new_status),
            requested_at=user.api_access_requested_at,
            decided_at=user.api_access_decided_at,
            use_case=user.api_access_use_case,
            denial_reason=user.api_access_denial_reason,
            message=messages.get(ApiAccessStatusEnum(new_status), "API access status updated."),
        )

    async def request_api_access(self, user_id: str, use_case: str) -> ApiAccessStatusResponse:
        """
        User requests API access with a use case description.

        Args:
            user_id: The user's ID
            use_case: Description of how they plan to use the API

        Returns:
            ApiAccessStatusResponse with PENDING status

        Raises:
            ValueError: If user not found, already pending, or already approved
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        current_status = user.api_access_status

        if current_status == ApiAccessStatus.SUSPENDED.value:
            raise ValueError("Your API access has been suspended. If you believe this is an error, please contact support at support@encypherai.com.")

        if current_status == ApiAccessStatus.PENDING.value:
            raise ValueError("API access request is already pending review")

        if current_status == ApiAccessStatus.APPROVED.value:
            raise ValueError("API access is already approved")

        user.api_access_status = ApiAccessStatus.PENDING.value
        user.api_access_use_case = use_case
        user.api_access_requested_at = datetime.now(timezone.utc)
        user.api_access_decided_at = None
        user.api_access_decided_by = None
        user.api_access_denial_reason = None

        self.db.commit()

        self._notify_admins_of_new_request(user)

        return ApiAccessStatusResponse(
            status=ApiAccessStatusEnum.PENDING,
            requested_at=user.api_access_requested_at,
            use_case=user.api_access_use_case,
            message="Your API access request has been submitted for review.",
        )

    def _notify_admins_of_new_request(self, user: User) -> None:
        """Send email notification about new API access request."""
        if not EMAIL_AVAILABLE:
            logger.warning("Email not available, skipping admin notification")
            return

        try:
            config = _get_email_config()
            requested_at = user.api_access_requested_at.strftime("%B %d, %Y at %I:%M %p UTC") if user.api_access_requested_at else "Just now"

            recipients = []
            if config.support_email:
                recipients.append(config.support_email)

            super_admins = self.db.query(User).filter(User.is_super_admin == True).all()
            for admin in super_admins:
                if admin.email not in recipients:
                    recipients.append(admin.email)

            if not recipients:
                logger.warning("No recipients configured for API access notifications")
                return

            for recipient in recipients:
                try:
                    send_api_access_request_admin_email(
                        config=config,
                        to_email=recipient,
                        requester_name=user.name,
                        requester_email=user.email,
                        use_case=user.api_access_use_case or "",
                        requested_at=requested_at,
                        logger=logger,
                    )
                    logger.info(f"Sent new API access request notification to {recipient}")
                except Exception as e:
                    logger.error(f"Failed to send notification to {recipient}: {e}")
        except Exception as e:
            logger.error(f"Failed to notify admins of new request: {e}")

    async def approve_api_access(self, user_id: str, admin_user_id: str) -> ApiAccessStatusResponse:
        """
        Admin approves a user's API access request.

        Args:
            user_id: The user to approve
            admin_user_id: The admin making the decision

        Returns:
            ApiAccessStatusResponse with APPROVED status

        Raises:
            ValueError: If user not found or request not pending
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        if user.api_access_status != ApiAccessStatus.PENDING.value:
            raise ValueError("API access request is not pending")

        user.api_access_status = ApiAccessStatus.APPROVED.value
        user.api_access_decided_at = datetime.now(timezone.utc)
        user.api_access_decided_by = admin_user_id
        user.api_access_denial_reason = None

        self.db.commit()

        self._send_approval_email(user)

        return ApiAccessStatusResponse(
            status=ApiAccessStatusEnum.APPROVED,
            requested_at=user.api_access_requested_at,
            decided_at=user.api_access_decided_at,
            use_case=user.api_access_use_case,
            message="API access has been approved.",
        )

    def _send_approval_email(self, user: User) -> None:
        """Send approval notification email to user."""
        if not EMAIL_AVAILABLE:
            logger.warning("Email not available, skipping approval notification")
            return

        try:
            config = _get_email_config()
            send_api_access_approved_email(
                config=config,
                to_email=user.email,
                user_name=user.name,
                logger=logger,
            )
            logger.info(f"Sent approval email to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send approval email to {user.email}: {e}")

    async def deny_api_access(self, user_id: str, admin_user_id: str, reason: str) -> ApiAccessStatusResponse:
        """
        Admin denies a user's API access request.

        Args:
            user_id: The user to deny
            admin_user_id: The admin making the decision
            reason: Reason for denial (shown to user)

        Returns:
            ApiAccessStatusResponse with DENIED status

        Raises:
            ValueError: If user not found or request not pending
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        if user.api_access_status != ApiAccessStatus.PENDING.value:
            raise ValueError("API access request is not pending")

        user.api_access_status = ApiAccessStatus.DENIED.value
        user.api_access_decided_at = datetime.now(timezone.utc)
        user.api_access_decided_by = admin_user_id
        user.api_access_denial_reason = reason

        self.db.commit()

        self._send_denial_email(user, reason)

        return ApiAccessStatusResponse(
            status=ApiAccessStatusEnum.DENIED,
            requested_at=user.api_access_requested_at,
            decided_at=user.api_access_decided_at,
            use_case=user.api_access_use_case,
            denial_reason=reason,
            message="API access request has been denied.",
        )

    def _send_denial_email(self, user: User, reason: str) -> None:
        """Send denial notification email to user."""
        if not EMAIL_AVAILABLE:
            logger.warning("Email not available, skipping denial notification")
            return

        try:
            config = _get_email_config()
            send_api_access_denied_email(
                config=config,
                to_email=user.email,
                user_name=user.name,
                denial_reason=reason,
                logger=logger,
            )
            logger.info(f"Sent denial email to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send denial email to {user.email}: {e}")
