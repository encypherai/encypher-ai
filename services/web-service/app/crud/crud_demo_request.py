
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.demo_request import DemoRequest
from app.schemas.demo_request import DemoRequestCreate, DemoRequestUpdate


class CRUDDemoRequest(CRUDBase[DemoRequest, DemoRequestCreate, DemoRequestUpdate]):
    """CRUD operations for DemoRequest model"""

    def create_with_metadata(
        self,
        db: Session,
        *,
        obj_in: DemoRequestCreate,
        ip_address: str | None = None,
        user_agent: str | None = None,
        referrer: str | None = None
    ) -> DemoRequest:
        """Create a new demo request with additional metadata"""
        # Convert the Pydantic model to a dict
        obj_in_data = obj_in.dict()

        # Add metadata
        if ip_address:
            obj_in_data["ip_address"] = ip_address
        if user_agent:
            obj_in_data["user_agent"] = user_agent
        if referrer:
            obj_in_data["referrer"] = referrer

        # Create the database object
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, *, email: str) -> DemoRequest | None:
        """Get a demo request by email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_multi_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> list[DemoRequest]:
        """Get multiple demo requests filtered by status"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

# Create an instance of the CRUDDemoRequest class
demo_request = CRUDDemoRequest(DemoRequest)
