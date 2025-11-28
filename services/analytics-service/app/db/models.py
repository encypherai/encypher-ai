"""SQLAlchemy database models for Analytics Service"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class UsageMetric(Base):
    """Usage metrics model"""
    __tablename__ = "usage_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=True, index=True)

    # Metric details
    metric_type = Column(String, nullable=False, index=True)  # api_call, document_signed, verification, etc.
    service_name = Column(String, nullable=False, index=True)
    endpoint = Column(String, nullable=True)

    # Counts and values
    count = Column(Integer, nullable=False, default=1)
    value = Column(Float, nullable=True)

    # Performance
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)

    # Metadata (renamed to avoid SQLAlchemy reserved attribute name)
    meta = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD for aggregation
    hour = Column(Integer, nullable=False, index=True)  # 0-23 for hourly aggregation

    def __repr__(self):
        return f"<UsageMetric(id={self.id}, metric_type={self.metric_type}, user_id={self.user_id})>"


class AggregatedMetric(Base):
    """Pre-aggregated metrics for performance"""
    __tablename__ = "aggregated_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True, index=True)
    organization_id = Column(String, nullable=True, index=True)

    # Aggregation details
    metric_type = Column(String, nullable=False, index=True)
    service_name = Column(String, nullable=False, index=True)
    aggregation_period = Column(String, nullable=False, index=True)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Aggregated values
    total_count = Column(Integer, nullable=False, default=0)
    total_value = Column(Float, nullable=True)
    avg_response_time_ms = Column(Float, nullable=True)
    min_response_time_ms = Column(Integer, nullable=True)
    max_response_time_ms = Column(Integer, nullable=True)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)

    # Metadata (renamed to avoid SQLAlchemy reserved attribute name)
    meta = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AggregatedMetric(id={self.id}, metric_type={self.metric_type}, period={self.aggregation_period})>"
