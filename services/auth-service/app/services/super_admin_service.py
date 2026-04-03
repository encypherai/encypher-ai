"""Ensure designated super admin account remains elevated."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User

SUPER_ADMIN_EMAIL = "erik.svilich@encypher.com"


def ensure_super_admin_user(db: Session) -> bool:
    """Ensure the designated super admin user is flagged as super admin."""
    target_email = settings.ADMIN_EMAIL or SUPER_ADMIN_EMAIL
    user = db.query(User).filter(User.email == target_email).first()
    if not user:
        return False

    if user.is_super_admin:
        return False

    user.is_super_admin = True
    db.commit()
    return True
