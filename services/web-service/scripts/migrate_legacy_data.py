import argparse
import logging
import sys

from sqlalchemy import create_engine, text

# Add app to path
sys.path.append(".")
from app.db.base import SessionLocal
from app.models.demo_request import DemoRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_demo_requests(legacy_db_url: str):
    """
    Migrate demo requests from legacy database to new web-service database.
    """
    logger.info(f"Connecting to legacy database: {legacy_db_url}")
    legacy_engine = create_engine(legacy_db_url)

    # Connect to new DB
    new_db = SessionLocal()

    try:
        with legacy_engine.connect() as conn:
            # Adjust query based on legacy schema
            result = conn.execute(text("SELECT * FROM demo_requests"))

            count = 0
            for row in result:
                # Check if already exists (by email and created_at, or uuid)
                existing = new_db.query(DemoRequest).filter(DemoRequest.email == row.email, DemoRequest.created_at == row.created_at).first()

                if existing:
                    logger.info(f"Skipping existing record: {row.email}")
                    continue

                # Map fields
                demo_req = DemoRequest(
                    uuid=row.uuid,
                    name=row.name,
                    email=row.email,
                    organization=row.organization,
                    role=row.role,
                    message=row.message,
                    source=row.source,
                    consent=bool(row.consent),
                    ip_address=row.ip_address,
                    user_agent=row.user_agent,
                    referrer=row.referrer,
                    created_at=row.created_at,
                    # Map other fields as needed
                )

                new_db.add(demo_req)
                count += 1

            new_db.commit()
            logger.info(f"Migrated {count} demo requests.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        new_db.rollback()
    finally:
        new_db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate legacy data")
    parser.add_argument("legacy_db_url", help="SQLAlchemy connection string for legacy DB")
    args = parser.parse_args()

    migrate_demo_requests(args.legacy_db_url)
