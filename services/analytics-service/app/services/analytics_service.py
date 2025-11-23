"""Analytics service business logic"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..db.models import UsageMetric
from ..models.schemas import MetricCreate


class AnalyticsService:
    """Analytics and metrics service"""
    
    @staticmethod
    def record_metric(
        db: Session,
        user_id: str,
        metric_data: MetricCreate,
        organization_id: Optional[str] = None,
    ) -> UsageMetric:
        """Record a usage metric"""
        now = datetime.utcnow()
        
        metric = UsageMetric(
            user_id=user_id,
            organization_id=organization_id,
            metric_type=metric_data.metric_type,
            service_name=metric_data.service_name,
            endpoint=metric_data.endpoint,
            count=metric_data.count,
            value=metric_data.value,
            response_time_ms=metric_data.response_time_ms,
            status_code=metric_data.status_code,
            meta=metric_data.metadata,
            date=now.strftime("%Y-%m-%d"),
            hour=now.hour,
        )
        
        db.add(metric)
        db.commit()
        db.refresh(metric)
        
        return metric
    
    @staticmethod
    def get_usage_stats(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        # Total API calls
        total_api_calls = db.query(func.sum(UsageMetric.count)).filter(
            and_(
                UsageMetric.user_id == user_id,
                UsageMetric.metric_type == "api_call",
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        ).scalar() or 0
        
        # Documents signed
        total_documents_signed = db.query(func.sum(UsageMetric.count)).filter(
            and_(
                UsageMetric.user_id == user_id,
                UsageMetric.metric_type == "document_signed",
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        ).scalar() or 0
        
        # Verifications
        total_verifications = db.query(func.sum(UsageMetric.count)).filter(
            and_(
                UsageMetric.user_id == user_id,
                UsageMetric.metric_type == "verification",
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        ).scalar() or 0
        
        # Keys generated
        total_keys_generated = db.query(func.sum(UsageMetric.count)).filter(
            and_(
                UsageMetric.user_id == user_id,
                UsageMetric.metric_type == "key_generated",
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        ).scalar() or 0
        
        return {
            "total_api_calls": int(total_api_calls),
            "total_documents_signed": int(total_documents_signed),
            "total_verifications": int(total_verifications),
            "total_keys_generated": int(total_keys_generated),
            "period_start": start_date,
            "period_end": end_date,
        }
    
    @staticmethod
    def get_service_metrics(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Get metrics grouped by service"""
        services = db.query(UsageMetric.service_name).filter(
            and_(
                UsageMetric.user_id == user_id,
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        ).distinct().all()
        
        service_metrics = []
        for (service_name,) in services:
            # Total requests
            total_requests = db.query(func.sum(UsageMetric.count)).filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.service_name == service_name,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            ).scalar() or 0
            
            # Success count (2xx status codes)
            success_count = db.query(func.sum(UsageMetric.count)).filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.service_name == service_name,
                    UsageMetric.status_code >= 200,
                    UsageMetric.status_code < 300,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            ).scalar() or 0
            
            # Error count
            error_count = db.query(func.sum(UsageMetric.count)).filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.service_name == service_name,
                    UsageMetric.status_code >= 400,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            ).scalar() or 0
            
            # Average response time
            avg_response_time = db.query(func.avg(UsageMetric.response_time_ms)).filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.service_name == service_name,
                    UsageMetric.response_time_ms.isnot(None),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            ).scalar() or 0.0
            
            # Endpoints
            endpoint_counts = db.query(
                UsageMetric.endpoint,
                func.sum(UsageMetric.count).label('count')
            ).filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.service_name == service_name,
                    UsageMetric.endpoint.isnot(None),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            ).group_by(UsageMetric.endpoint).all()
            
            endpoints = {endpoint: int(count) for endpoint, count in endpoint_counts}
            
            service_metrics.append({
                "service_name": service_name,
                "total_requests": int(total_requests),
                "success_count": int(success_count),
                "error_count": int(error_count),
                "avg_response_time_ms": float(avg_response_time),
                "endpoints": endpoints,
            })
        
        return service_metrics
    
    @staticmethod
    def get_time_series(
        db: Session,
        user_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "hour",
    ) -> List[Dict[str, Any]]:
        """Get time series data"""
        if interval == "hour":
            # Group by date and hour
            results = db.query(
                UsageMetric.date,
                UsageMetric.hour,
                func.sum(UsageMetric.count).label('count'),
                func.sum(UsageMetric.value).label('value'),
            ).filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.metric_type == metric_type,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            ).group_by(UsageMetric.date, UsageMetric.hour).order_by(UsageMetric.date, UsageMetric.hour).all()
            
            time_series = []
            for date_str, hour, count, value in results:
                timestamp = datetime.strptime(f"{date_str} {hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
                time_series.append({
                    "timestamp": timestamp,
                    "count": int(count or 0),
                    "value": float(value or 0.0),
                })
            
            return time_series
        
        # Daily aggregation
        results = db.query(
            UsageMetric.date,
            func.sum(UsageMetric.count).label('count'),
            func.sum(UsageMetric.value).label('value'),
        ).filter(
            and_(
                UsageMetric.user_id == user_id,
                UsageMetric.metric_type == metric_type,
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        ).group_by(UsageMetric.date).order_by(UsageMetric.date).all()
        
        time_series = []
        for date_str, count, value in results:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d")
            time_series.append({
                "timestamp": timestamp,
                "count": int(count or 0),
                "value": float(value or 0.0),
            })
        
        return time_series
