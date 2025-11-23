from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.analytics_event import AnalyticsEvent
from app.schemas.analytics_event import AnalyticsEventCreate, AnalyticsEventUpdate, AnalyticsEventType

class CRUDAnalyticsEvent(CRUDBase[AnalyticsEvent, AnalyticsEventCreate, AnalyticsEventUpdate]):
    """CRUD operations for AnalyticsEvent model"""
    
    def create_with_metadata(
        self, 
        db: Session, 
        *, 
        obj_in: AnalyticsEventCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_id: Optional[str] = None,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        os: Optional[str] = None
    ) -> AnalyticsEvent:
        """Create a new analytics event with additional metadata"""
        # Convert the Pydantic model to a dict
        obj_in_data = obj_in.dict(exclude_unset=True)
        
        # Add or override metadata
        if ip_address:
            obj_in_data["ip_address"] = ip_address
        if user_agent:
            obj_in_data["user_agent"] = user_agent
        if user_id:
            obj_in_data["user_id"] = user_id
        if device_type:
            obj_in_data["device_type"] = device_type
        if browser:
            obj_in_data["browser"] = browser
        if os:
            obj_in_data["os"] = os
        
        # Create the database object
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_events_by_session(
        self, db: Session, *, session_id: str, limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Get all events for a specific session"""
        return (
            db.query(self.model)
            .filter(self.model.session_id == session_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_events_by_user(
        self, db: Session, *, user_id: str, limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Get all events for a specific user"""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_events_by_type(
        self, db: Session, *, event_type: str, limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Get all events of a specific type"""
        return (
            db.query(self.model)
            .filter(self.model.event_type == event_type)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_page_views(
        self, 
        db: Session, 
        *, 
        page_url: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Get page view events with optional filters"""
        query = db.query(self.model).filter(
            self.model.event_type == AnalyticsEventType.PAGE_VIEW
        )
        
        if page_url:
            query = query.filter(self.model.page_url.like(f"%{page_url}%"))
        
        if start_date:
            query = query.filter(self.model.created_at >= start_date)
        
        if end_date:
            query = query.filter(self.model.created_at <= end_date)
        
        return query.order_by(self.model.created_at.desc()).limit(limit).all()
    
    def get_event_counts_by_type(
        self, 
        db: Session, 
        *, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get counts of events grouped by event type"""
        query = db.query(
            self.model.event_type, 
            func.count(self.model.id).label("count")
        ).group_by(self.model.event_type)
        
        if start_date:
            query = query.filter(self.model.created_at >= start_date)
        
        if end_date:
            query = query.filter(self.model.created_at <= end_date)
        
        result = query.all()
        return {row[0]: row[1] for row in result}

# Create an instance of the CRUDAnalyticsEvent class
analytics_event = CRUDAnalyticsEvent(AnalyticsEvent)
