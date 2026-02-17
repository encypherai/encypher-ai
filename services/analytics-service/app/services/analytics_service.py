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
        """Get usage statistics for a user or organization.

        Args:
            user_id: User ID or organization ID to query
        """
        from sqlalchemy import or_

        # Query by both user_id and organization_id for compatibility
        def user_or_org_filter():
            return or_(
                UsageMetric.user_id == user_id,
                UsageMetric.organization_id == user_id,
            )

        # Total API calls
        total_api_calls = (
            db.query(func.sum(UsageMetric.count))
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.metric_type.in_(["api_call", "API_CALL"]),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .scalar()
            or 0
        )

        # Documents signed
        total_documents_signed = (
            db.query(func.sum(UsageMetric.count))
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.metric_type.in_(["document_signed", "DOCUMENT_SIGNED"]),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .scalar()
            or 0
        )

        # Verifications
        total_verifications = (
            db.query(func.sum(UsageMetric.count))
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.metric_type.in_(["verification", "document_verified", "DOCUMENT_VERIFIED"]),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .scalar()
            or 0
        )

        # Calculate success rate from status codes
        total_requests = (
            db.query(func.count(UsageMetric.id))
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.status_code.isnot(None),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .scalar()
            or 0
        )

        successful_requests = (
            db.query(func.count(UsageMetric.id))
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.status_code >= 200,
                    UsageMetric.status_code < 400,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .scalar()
            or 0
        )

        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0.0

        # Average response time
        avg_response_time = (
            db.query(func.avg(UsageMetric.response_time_ms))
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.response_time_ms.isnot(None),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .scalar()
            or 0.0
        )

        return {
            "total_api_calls": int(total_api_calls) or int(total_documents_signed + total_verifications),
            "total_documents_signed": int(total_documents_signed),
            "total_verifications": int(total_verifications),
            "success_rate": float(success_rate),
            "avg_response_time_ms": float(avg_response_time),
            "total_keys_generated": 0,
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
        services = (
            db.query(UsageMetric.service_name)
            .filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .distinct()
            .all()
        )
        service_metrics = []
        for (service_name,) in services:
            # Total requests
            total_requests = (
                db.query(func.sum(UsageMetric.count))
                .filter(
                    and_(
                        UsageMetric.user_id == user_id,
                        UsageMetric.service_name == service_name,
                        UsageMetric.created_at >= start_date,
                        UsageMetric.created_at <= end_date,
                    )
                )
                .scalar()
                or 0
            )

            # Success count (2xx status codes)
            success_count = (
                db.query(func.sum(UsageMetric.count))
                .filter(
                    and_(
                        UsageMetric.user_id == user_id,
                        UsageMetric.service_name == service_name,
                        UsageMetric.status_code >= 200,
                        UsageMetric.status_code < 300,
                        UsageMetric.created_at >= start_date,
                        UsageMetric.created_at <= end_date,
                    )
                )
                .scalar()
                or 0
            )

            # Error count
            error_count = (
                db.query(func.sum(UsageMetric.count))
                .filter(
                    and_(
                        UsageMetric.user_id == user_id,
                        UsageMetric.service_name == service_name,
                        UsageMetric.status_code >= 400,
                        UsageMetric.created_at >= start_date,
                        UsageMetric.created_at <= end_date,
                    )
                )
                .scalar()
                or 0
            )

            # Average response time
            avg_response_time = (
                db.query(func.avg(UsageMetric.response_time_ms))
                .filter(
                    and_(
                        UsageMetric.user_id == user_id,
                        UsageMetric.service_name == service_name,
                        UsageMetric.response_time_ms.isnot(None),
                        UsageMetric.created_at >= start_date,
                        UsageMetric.created_at <= end_date,
                    )
                )
                .scalar()
                or 0.0
            )

            # Endpoints
            endpoint_counts = (
                db.query(UsageMetric.endpoint, func.sum(UsageMetric.count).label("count"))
                .filter(
                    and_(
                        UsageMetric.user_id == user_id,
                        UsageMetric.service_name == service_name,
                        UsageMetric.endpoint.isnot(None),
                        UsageMetric.created_at >= start_date,
                        UsageMetric.created_at <= end_date,
                    )
                )
                .group_by(UsageMetric.endpoint)
                .all()
            )

            endpoints = {endpoint: int(count) for endpoint, count in endpoint_counts}

            service_metrics.append(
                {
                    "service_name": service_name,
                    "total_requests": int(total_requests),
                    "success_count": int(success_count),
                    "error_count": int(error_count),
                    "avg_response_time_ms": float(avg_response_time),
                    "endpoints": endpoints,
                }
            )

        return service_metrics

    @staticmethod
    def get_activity_events(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        page: int,
        limit: int,
        api_key_prefix: Optional[str] = None,
        endpoint: Optional[str] = None,
        status: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        query: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        has_stack: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get paginated activity events with audit-oriented filters."""
        metric_query = AnalyticsService._build_activity_query(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            api_key_prefix=api_key_prefix,
            endpoint=endpoint,
            status=status,
            error_code=error_code,
            request_id=request_id,
            event_type=event_type,
            actor_id=actor_id,
            query=query,
            event_types=event_types,
            severities=severities,
            has_stack=has_stack,
        )

        total = metric_query.count()
        offset = (page - 1) * limit
        items = metric_query.order_by(UsageMetric.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
        }

    @staticmethod
    def get_activity_export_rows(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        api_key_prefix: Optional[str] = None,
        endpoint: Optional[str] = None,
        status: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        query: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        has_stack: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Get flattened activity rows for CSV/JSON export."""
        metric_query = AnalyticsService._build_activity_query(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            api_key_prefix=api_key_prefix,
            endpoint=endpoint,
            status=status,
            error_code=error_code,
            request_id=request_id,
            event_type=event_type,
            actor_id=actor_id,
            query=query,
            event_types=event_types,
            severities=severities,
            has_stack=has_stack,
        )

        rows: List[Dict[str, Any]] = []
        for metric in metric_query.order_by(UsageMetric.created_at.desc()).all():
            payload = AnalyticsService.describe_activity(metric)
            metadata = payload.get("metadata") if isinstance(payload, dict) else None
            metadata = metadata if isinstance(metadata, dict) else {}
            rows.append(
                {
                    "id": payload.get("id"),
                    "timestamp": payload.get("timestamp"),
                    "type": payload.get("type"),
                    "description": payload.get("description"),
                    "status": metadata.get("status"),
                    "severity": metadata.get("severity"),
                    "endpoint": metadata.get("endpoint"),
                    "method": metadata.get("method"),
                    "request_id": metadata.get("request_id"),
                    "api_key": metadata.get("api_key"),
                    "error_code": metadata.get("error_code"),
                    "error_message": metadata.get("error_message"),
                    "error_details": metadata.get("error_details"),
                    "error_stack": metadata.get("error_stack"),
                    "event_type": metadata.get("event_type"),
                    "actor_type": metadata.get("actor_type"),
                    "actor_id": metadata.get("actor_id"),
                    "resource_type": metadata.get("resource_type"),
                    "resource_id": metadata.get("resource_id"),
                    "organization_id": metadata.get("organization_id"),
                }
            )
        return rows

    @staticmethod
    def get_activity_alert_summary(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Aggregate audit-alert summary statistics for dashboard visibility."""
        query = AnalyticsService._build_activity_query(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        metrics = query.all()

        total_requests = len(metrics)
        failure_metrics = [m for m in metrics if m.status_code is not None and m.status_code >= 400]
        critical_failures = [m for m in metrics if m.status_code is not None and m.status_code >= 500]
        failure_requests = len(failure_metrics)
        failure_rate = round((failure_requests / total_requests) * 100, 2) if total_requests > 0 else 0.0

        error_counts: Dict[str, int] = {}
        for metric in failure_metrics:
            meta = metric.meta if isinstance(metric.meta, dict) else {}
            code = meta.get("error_code") or "UNKNOWN"
            error_counts[code] = error_counts.get(code, 0) + 1

        top_error_codes = [
            {"error_code": code, "count": count}
            for code, count in sorted(error_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        ]

        return {
            "total_requests": total_requests,
            "failure_requests": failure_requests,
            "critical_failures": len(critical_failures),
            "failure_rate": failure_rate,
            "top_error_codes": top_error_codes,
            "period_start": start_date,
            "period_end": end_date,
        }

    @staticmethod
    def _build_activity_query(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        api_key_prefix: Optional[str] = None,
        endpoint: Optional[str] = None,
        status: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        query: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        has_stack: Optional[bool] = None,
    ):
        """Build filtered query used by audit activity endpoints and exports."""
        from sqlalchemy import or_

        def user_or_org_filter():
            return or_(
                UsageMetric.user_id == user_id,
                UsageMetric.organization_id == user_id,
            )

        metric_query = db.query(UsageMetric).filter(
            and_(
                user_or_org_filter(),
                UsageMetric.created_at >= start_date,
                UsageMetric.created_at <= end_date,
            )
        )

        if endpoint:
            metric_query = metric_query.filter(UsageMetric.endpoint.ilike(f"%{endpoint}%"))

        if status == "success":
            metric_query = metric_query.filter(and_(UsageMetric.status_code >= 200, UsageMetric.status_code < 400))
        elif status == "failure":
            metric_query = metric_query.filter(UsageMetric.status_code >= 400)

        if api_key_prefix:
            metric_query = metric_query.filter(UsageMetric.meta["api_key_prefix"].as_string() == api_key_prefix)
        if error_code:
            metric_query = metric_query.filter(UsageMetric.meta["error_code"].as_string() == error_code)
        if request_id:
            metric_query = metric_query.filter(UsageMetric.meta["request_id"].as_string() == request_id)
        if event_type:
            metric_query = metric_query.filter(UsageMetric.meta["event_type"].as_string() == event_type)
        if actor_id:
            metric_query = metric_query.filter(UsageMetric.meta["actor_id"].as_string() == actor_id)

        if query:
            search_value = f"%{query}%"
            metric_query = metric_query.filter(
                or_(
                    UsageMetric.endpoint.ilike(search_value),
                    UsageMetric.metric_type.ilike(search_value),
                    UsageMetric.meta["request_id"].as_string().ilike(search_value),
                    UsageMetric.meta["error_code"].as_string().ilike(search_value),
                    UsageMetric.meta["error_message"].as_string().ilike(search_value),
                    UsageMetric.meta["error_details"].as_string().ilike(search_value),
                    UsageMetric.meta["event_type"].as_string().ilike(search_value),
                    UsageMetric.meta["actor_id"].as_string().ilike(search_value),
                )
            )

        if event_types:
            metric_query = metric_query.filter(
                or_(
                    UsageMetric.meta["event_type"].as_string().in_(event_types),
                    UsageMetric.metric_type.in_(event_types),
                )
            )

        if severities:
            normalized = {value.lower() for value in severities if value}
            severity_conditions = []
            if "critical" in normalized:
                severity_conditions.append(UsageMetric.status_code >= 500)
            if "high" in normalized:
                severity_conditions.append(
                    and_(UsageMetric.status_code >= 400, UsageMetric.status_code < 500)
                )
            if "medium" in normalized:
                severity_conditions.append(
                    and_(
                        or_(UsageMetric.status_code.is_(None), UsageMetric.status_code < 400),
                        func.lower(UsageMetric.metric_type).in_(["admin_action", "security_event"]),
                    )
                )
            if "low" in normalized:
                severity_conditions.append(
                    and_(
                        or_(UsageMetric.status_code.is_(None), UsageMetric.status_code < 400),
                        ~func.lower(UsageMetric.metric_type).in_(["admin_action", "security_event"]),
                    )
                )
            if severity_conditions:
                metric_query = metric_query.filter(or_(*severity_conditions))

        if has_stack is True:
            metric_query = metric_query.filter(
                and_(
                    UsageMetric.meta["error_stack"].as_string().isnot(None),
                    UsageMetric.meta["error_stack"].as_string() != "",
                )
            )

        return metric_query

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
            results = (
                db.query(
                    UsageMetric.date,
                    UsageMetric.hour,
                    func.sum(UsageMetric.count).label("count"),
                    func.sum(UsageMetric.value).label("value"),
                )
                .filter(
                    and_(
                        UsageMetric.user_id == user_id,
                        UsageMetric.metric_type == metric_type,
                        UsageMetric.created_at >= start_date,
                        UsageMetric.created_at <= end_date,
                    )
                )
                .group_by(UsageMetric.date, UsageMetric.hour)
                .order_by(UsageMetric.date, UsageMetric.hour)
                .all()
            )

            time_series = []
            for date_str, hour, count, value in results:
                timestamp = datetime.strptime(f"{date_str} {hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
                time_series.append(
                    {
                        "timestamp": timestamp,
                        "count": int(count or 0),
                        "value": float(value or 0.0),
                    }
                )

            return time_series

        results = (
            db.query(
                UsageMetric.date,
                func.sum(UsageMetric.count).label("count"),
                func.sum(UsageMetric.value).label("value"),
            )
            .filter(
                and_(
                    UsageMetric.user_id == user_id,
                    UsageMetric.metric_type == metric_type,
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .group_by(UsageMetric.date)
            .order_by(UsageMetric.date)
            .all()
        )

        time_series = []
        for date_str, count, value in results:
            timestamp = datetime.strptime(str(date_str), "%Y-%m-%d")
            time_series.append(
                {
                    "timestamp": timestamp,
                    "count": int(count or 0),
                    "value": float(value or 0.0),
                }
            )

        return time_series

    @staticmethod
    def get_activity_feed(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
    ) -> List[UsageMetric]:
        """Get recent activity items for a user or organization."""
        from sqlalchemy import or_

        def user_or_org_filter():
            return or_(
                UsageMetric.user_id == user_id,
                UsageMetric.organization_id == user_id,
            )

        return (
            db.query(UsageMetric)
            .filter(
                and_(
                    user_or_org_filter(),
                    UsageMetric.created_at >= start_date,
                    UsageMetric.created_at <= end_date,
                )
            )
            .order_by(UsageMetric.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def describe_activity(metric: UsageMetric) -> Dict[str, Any]:
        """Map a UsageMetric into dashboard activity feed fields."""
        metric_type = (metric.metric_type or "").lower()
        status_code = metric.status_code
        endpoint = metric.endpoint or ""
        metric_meta = metric.meta if isinstance(metric.meta, dict) else {}
        description = "API call completed"
        activity_type = "api_call"

        if "document_signed" in metric_type or "sign" in endpoint:
            description = "Signing request completed"
            activity_type = "sign"
        elif "document_verified" in metric_type or "verify" in endpoint:
            description = "Verification request completed"
            activity_type = "verify"

        if status_code is not None and status_code >= 400:
            description = f"Request failed with status {status_code}"
            activity_type = "api_call"

        severity = "low"
        if status_code is not None and status_code >= 500:
            severity = "critical"
        elif status_code is not None and status_code >= 400:
            severity = "high"
        elif metric_type in {"admin_action", "security_event"}:
            severity = "medium"

        metadata: Dict[str, Any] = {
            "status": status_code,
            "latency_ms": metric.response_time_ms,
            "endpoint": endpoint or None,
            "method": metric_meta.get("method"),
            "region": metric_meta.get("region"),
            "request_id": metric_meta.get("request_id"),
            "api_key": metric_meta.get("api_key_prefix"),
            "error_code": metric_meta.get("error_code"),
            "error_message": metric_meta.get("error_message"),
            "error_details": metric_meta.get("error_details"),
            "error_stack": metric_meta.get("error_stack"),
            "event_type": metric_meta.get("event_type") or metric_type,
            "actor_type": metric_meta.get("actor_type") or "api_key",
            "actor_id": metric_meta.get("actor_id") or metric.user_id,
            "resource_type": metric_meta.get("resource_type"),
            "resource_id": metric_meta.get("resource_id"),
            "organization_id": metric.organization_id,
            "severity": severity,
        }

        return {
            "id": metric.id,
            "type": activity_type,
            "description": description,
            "timestamp": metric.created_at,
            "metadata": {k: v for k, v in metadata.items() if v is not None},
        }
