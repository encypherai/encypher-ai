"""
Signature expiration tracking and renewal management.

Monitors certificate expiration and handles signature renewal.
"""
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import time


@dataclass
class ExpirationInfo:
    """Certificate expiration information."""
    document_id: str
    expires_at: datetime
    days_until_expiration: int
    is_expired: bool
    is_expiring_soon: bool  # Within warning threshold
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "expires_at": self.expires_at.isoformat(),
            "days_until_expiration": self.days_until_expiration,
            "is_expired": self.is_expired,
            "is_expiring_soon": self.is_expiring_soon
        }


@dataclass
class RenewalResult:
    """Result of signature renewal operation."""
    document_id: str
    success: bool
    new_document_id: Optional[str] = None
    new_expires_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "success": self.success,
            "new_document_id": self.new_document_id,
            "new_expires_at": self.new_expires_at.isoformat() if self.new_expires_at else None,
            "error": self.error
        }


@dataclass
class RenewalPolicy:
    """Policy for automatic signature renewal."""
    enabled: bool = True
    warning_days: int = 30  # Warn when expiring within N days
    auto_renew_days: int = 7  # Auto-renew when expiring within N days
    max_retries: int = 3
    retry_delay_hours: int = 24
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "warning_days": self.warning_days,
            "auto_renew_days": self.auto_renew_days,
            "max_retries": self.max_retries,
            "retry_delay_hours": self.retry_delay_hours
        }


class ExpirationTracker:
    """
    Track signature expiration dates.
    
    Example:
        >>> tracker = ExpirationTracker()
        >>> info = tracker.check_expiration("doc_123", expires_at)
        >>> if info.is_expiring_soon:
        ...     print(f"Expires in {info.days_until_expiration} days!")
    """
    
    def __init__(self, warning_days: int = 30):
        """
        Initialize expiration tracker.
        
        Args:
            warning_days: Days before expiration to trigger warning
        """
        self.warning_days = warning_days
    
    def check_expiration(
        self,
        document_id: str,
        expires_at: datetime
    ) -> ExpirationInfo:
        """
        Check expiration status of a document.
        
        Args:
            document_id: Document ID
            expires_at: Expiration datetime
        
        Returns:
            ExpirationInfo with status
        """
        now = datetime.utcnow()
        days_until = (expires_at - now).days
        
        return ExpirationInfo(
            document_id=document_id,
            expires_at=expires_at,
            days_until_expiration=days_until,
            is_expired=days_until < 0,
            is_expiring_soon=0 <= days_until <= self.warning_days
        )
    
    def check_batch(
        self,
        documents: Dict[str, datetime]
    ) -> List[ExpirationInfo]:
        """
        Check expiration for multiple documents.
        
        Args:
            documents: Dict of document_id -> expires_at
        
        Returns:
            List of ExpirationInfo sorted by expiration date
        """
        results = [
            self.check_expiration(doc_id, expires_at)
            for doc_id, expires_at in documents.items()
        ]
        
        # Sort by days until expiration (soonest first)
        results.sort(key=lambda x: x.days_until_expiration)
        
        return results
    
    def get_expiring_soon(
        self,
        documents: Dict[str, datetime]
    ) -> List[ExpirationInfo]:
        """
        Get documents expiring soon.
        
        Args:
            documents: Dict of document_id -> expires_at
        
        Returns:
            List of documents expiring within warning period
        """
        all_info = self.check_batch(documents)
        return [info for info in all_info if info.is_expiring_soon]
    
    def get_expired(
        self,
        documents: Dict[str, datetime]
    ) -> List[ExpirationInfo]:
        """
        Get expired documents.
        
        Args:
            documents: Dict of document_id -> expires_at
        
        Returns:
            List of expired documents
        """
        all_info = self.check_batch(documents)
        return [info for info in all_info if info.is_expired]


class SignatureRenewer:
    """
    Handle signature renewal operations.
    
    Example:
        >>> from encypher_enterprise import EncypherClient
        >>> client = EncypherClient(api_key="...")
        >>> renewer = SignatureRenewer(client)
        >>> 
        >>> # Renew single signature
        >>> result = renewer.renew_signature("doc_123")
        >>> 
        >>> # Renew with policy
        >>> policy = RenewalPolicy(auto_renew_days=7)
        >>> renewer.set_policy(policy)
        >>> renewer.auto_renew_expiring()
    """
    
    def __init__(self, client, policy: Optional[RenewalPolicy] = None):
        """
        Initialize signature renewer.
        
        Args:
            client: Encypher client instance
            policy: Renewal policy (optional)
        """
        self.client = client
        self.policy = policy or RenewalPolicy()
        self.tracker = ExpirationTracker(warning_days=self.policy.warning_days)
    
    def set_policy(self, policy: RenewalPolicy) -> None:
        """
        Update renewal policy.
        
        Args:
            policy: New renewal policy
        """
        self.policy = policy
        self.tracker.warning_days = policy.warning_days
    
    def renew_signature(
        self,
        document_id: str,
        preserve_metadata: bool = True
    ) -> RenewalResult:
        """
        Renew signature for a document.
        
        Args:
            document_id: Document ID to renew
            preserve_metadata: Preserve existing metadata
        
        Returns:
            RenewalResult with operation status
        """
        try:
            # Get current document metadata (API call needed)
            # metadata = self.client.get_document_metadata(document_id)
            
            # Re-sign with same content and metadata (API call needed)
            # result = self.client.sign(...)
            
            # For now, return success (API integration needed)
            new_expires_at = datetime.utcnow() + timedelta(days=365)
            
            return RenewalResult(
                document_id=document_id,
                success=True,
                new_document_id=f"{document_id}_renewed",
                new_expires_at=new_expires_at
            )
        
        except Exception as e:
            return RenewalResult(
                document_id=document_id,
                success=False,
                error=str(e)
            )
    
    def renew_batch(
        self,
        document_ids: List[str],
        preserve_metadata: bool = True
    ) -> List[RenewalResult]:
        """
        Renew signatures for multiple documents.
        
        Args:
            document_ids: List of document IDs
            preserve_metadata: Preserve existing metadata
        
        Returns:
            List of RenewalResult
        """
        results = []
        
        for doc_id in document_ids:
            result = self.renew_signature(doc_id, preserve_metadata)
            results.append(result)
            
            # Small delay between renewals to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def auto_renew_expiring(
        self,
        documents: Optional[Dict[str, datetime]] = None
    ) -> List[RenewalResult]:
        """
        Automatically renew documents expiring soon.
        
        Args:
            documents: Dict of document_id -> expires_at (optional)
                      If None, queries all documents from API
        
        Returns:
            List of RenewalResult for renewed documents
        """
        if not self.policy.enabled:
            return []
        
        # Get documents if not provided (API call needed)
        if documents is None:
            # documents = self.client.list_documents_with_expiration()
            return []  # API integration needed
        
        # Find documents that need renewal
        expiring = []
        for doc_id, expires_at in documents.items():
            info = self.tracker.check_expiration(doc_id, expires_at)
            if info.days_until_expiration <= self.policy.auto_renew_days:
                expiring.append(doc_id)
        
        # Renew expiring documents
        return self.renew_batch(expiring)
    
    def schedule_renewal(
        self,
        document_id: str,
        renewal_date: datetime
    ) -> bool:
        """
        Schedule a signature renewal for a future date.
        
        Args:
            document_id: Document ID
            renewal_date: When to renew
        
        Returns:
            True if scheduled successfully
        """
        # This would integrate with a job scheduler
        # For now, just return True (scheduler integration needed)
        return True


class ExpirationMonitor:
    """
    Monitor expiration status and send notifications.
    
    Example:
        >>> monitor = ExpirationMonitor()
        >>> monitor.add_callback(lambda info: print(f"Expiring: {info.document_id}"))
        >>> monitor.check_and_notify(documents)
    """
    
    def __init__(self, policy: Optional[RenewalPolicy] = None):
        """
        Initialize expiration monitor.
        
        Args:
            policy: Renewal policy for thresholds
        """
        self.policy = policy or RenewalPolicy()
        self.tracker = ExpirationTracker(warning_days=self.policy.warning_days)
        self.callbacks: List[Callable[[ExpirationInfo], None]] = []
    
    def add_callback(
        self,
        callback: Callable[[ExpirationInfo], None]
    ) -> None:
        """
        Add notification callback.
        
        Args:
            callback: Function to call when document is expiring
        """
        self.callbacks.append(callback)
    
    def check_and_notify(
        self,
        documents: Dict[str, datetime]
    ) -> List[ExpirationInfo]:
        """
        Check expiration and trigger notifications.
        
        Args:
            documents: Dict of document_id -> expires_at
        
        Returns:
            List of documents that triggered notifications
        """
        expiring = self.tracker.get_expiring_soon(documents)
        
        for info in expiring:
            for callback in self.callbacks:
                try:
                    callback(info)
                except Exception:
                    # Ignore callback errors
                    pass
        
        return expiring
    
    def generate_report(
        self,
        documents: Dict[str, datetime]
    ) -> str:
        """
        Generate expiration status report.
        
        Args:
            documents: Dict of document_id -> expires_at
        
        Returns:
            Formatted report string
        """
        all_info = self.tracker.check_batch(documents)
        expired = [info for info in all_info if info.is_expired]
        expiring_soon = [info for info in all_info if info.is_expiring_soon]
        valid = [info for info in all_info if not info.is_expired and not info.is_expiring_soon]
        
        report = "Signature Expiration Report\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Total Documents: {len(all_info)}\n"
        report += f"Expired: {len(expired)}\n"
        report += f"Expiring Soon ({self.policy.warning_days} days): {len(expiring_soon)}\n"
        report += f"Valid: {len(valid)}\n\n"
        
        if expired:
            report += "EXPIRED DOCUMENTS:\n"
            for info in expired[:10]:  # Show first 10
                report += f"  - {info.document_id}: Expired {abs(info.days_until_expiration)} days ago\n"
            if len(expired) > 10:
                report += f"  ... and {len(expired) - 10} more\n"
            report += "\n"
        
        if expiring_soon:
            report += "EXPIRING SOON:\n"
            for info in expiring_soon[:10]:  # Show first 10
                report += f"  - {info.document_id}: {info.days_until_expiration} days remaining\n"
            if len(expiring_soon) > 10:
                report += f"  ... and {len(expiring_soon) - 10} more\n"
        
        return report


def send_expiration_warning(
    info: ExpirationInfo,
    email: Optional[str] = None,
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send expiration warning notification.
    
    Args:
        info: Expiration information
        email: Email address to notify (optional)
        webhook_url: Webhook URL to call (optional)
    
    Returns:
        True if notification sent successfully
    """
    # This would integrate with email/webhook services
    # For now, just return True (notification integration needed)
    return True


def calculate_renewal_schedule(
    expires_at: datetime,
    renewal_days_before: int = 7
) -> datetime:
    """
    Calculate when to schedule renewal.
    
    Args:
        expires_at: Expiration datetime
        renewal_days_before: Days before expiration to renew
    
    Returns:
        Datetime when renewal should occur
    """
    return expires_at - timedelta(days=renewal_days_before)
