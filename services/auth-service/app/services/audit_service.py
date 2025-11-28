"""
Audit logging service for tracking security-critical operations.
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, Dict, List
import structlog

from ..models.audit_log import AuditLog

logger = structlog.get_logger()


class AuditService:
    """
    Service for creating and querying audit logs.
    
    Usage:
        audit = AuditService(db)
        await audit.log(
            action="user.login",
            resource_type="user",
            resource_id=user.id,
            organization_id=user.organization_id,
            result="success"
        )
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        result: str = "success",
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            action: Action performed (e.g., "user.login", "document.sign")
            resource_type: Type of resource (e.g., "user", "document")
            result: "success" or "failure"
            user_id: ID of user performing action
            organization_id: ID of organization
            resource_id: ID of resource being acted upon
            ip_address: IP address of request
            user_agent: User agent string
            request_id: Request ID for correlation
            details: Additional context as dictionary
            error_message: Error message if result is "failure"
            
        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details,
            result=result,
            error_message=error_message
        )

        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)

        # Also log to structured logger
        logger.info(
            "audit_log_created",
            audit_id=audit_log.id,
            action=action,
            resource_type=resource_type,
            result=result
        )

        return audit_log

    async def query_logs(
        self,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        result: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Query audit logs with filters.
        
        Args:
            organization_id: Filter by organization
            user_id: Filter by user
            action: Filter by action
            resource_type: Filter by resource type
            result: Filter by result (success/failure)
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of AuditLog instances
        """
        query = select(AuditLog)

        # Build filters
        filters = []
        if organization_id:
            filters.append(AuditLog.organization_id == organization_id)
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action == action)
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        if result:
            filters.append(AuditLog.result == result)
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)

        if filters:
            query = query.where(and_(*filters))

        # Order by timestamp descending
        query = query.order_by(AuditLog.timestamp.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_security_events(
        self,
        organization_id: str,
        hours: int = 24
    ) -> List[AuditLog]:
        """
        Get recent security-critical events for an organization.
        
        Args:
            organization_id: Organization ID
            hours: Number of hours to look back
            
        Returns:
            List of security-critical audit logs
        """
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(hours=hours)

        # Security-critical actions
        security_actions = [
            "user.login",
            "user.login_failed",
            "user.logout",
            "user.password_reset",
            "api_key.created",
            "api_key.revoked",
            "api_key.rotated",
            "permission.changed"
        ]

        query = select(AuditLog).where(
            and_(
                AuditLog.organization_id == organization_id,
                AuditLog.timestamp >= start_date,
                or_(*[AuditLog.action == action for action in security_actions])
            )
        ).order_by(AuditLog.timestamp.desc())

        result = await self.db.execute(query)
        return result.scalars().all()
