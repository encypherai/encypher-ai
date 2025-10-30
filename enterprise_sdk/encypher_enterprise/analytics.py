"""
Analytics and metrics tracking for signing and verification operations.

Provides usage tracking, performance metrics, and dashboard integration.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class OperationMetric:
    """Metric for a single operation."""
    operation_type: str  # sign, verify, lookup
    timestamp: datetime
    duration_ms: float
    success: bool
    document_id: Optional[str] = None
    error_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "operation_type": self.operation_type,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "document_id": self.document_id,
            "error_type": self.error_type,
            "metadata": self.metadata
        }


@dataclass
class UsageStats:
    """Usage statistics for a time period."""
    period_start: datetime
    period_end: datetime
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_documents_signed: int = 0
    total_verifications: int = 0
    total_lookups: int = 0
    avg_duration_ms: float = 0.0
    error_rate: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "total_documents_signed": self.total_documents_signed,
            "total_verifications": self.total_verifications,
            "total_lookups": self.total_lookups,
            "avg_duration_ms": self.avg_duration_ms,
            "error_rate": self.error_rate
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    p50_latency_ms: float  # Median
    p95_latency_ms: float  # 95th percentile
    p99_latency_ms: float  # 99th percentile
    min_latency_ms: float
    max_latency_ms: float
    avg_latency_ms: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "p50_latency_ms": self.p50_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "min_latency_ms": self.min_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "avg_latency_ms": self.avg_latency_ms
        }


class MetricsCollector:
    """
    Collect and store operation metrics.
    
    Example:
        >>> collector = MetricsCollector()
        >>> collector.record_operation("sign", 150.5, True, "doc_123")
        >>> stats = collector.get_stats(period_hours=24)
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize metrics collector.
        
        Args:
            storage_path: Path to store metrics (optional)
        """
        self.storage_path = storage_path
        self.metrics: List[OperationMetric] = []
        
        # Load existing metrics if storage path provided
        if storage_path and storage_path.exists():
            self._load_metrics()
    
    def record_operation(
        self,
        operation_type: str,
        duration_ms: float,
        success: bool,
        document_id: Optional[str] = None,
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record an operation metric.
        
        Args:
            operation_type: Type of operation (sign, verify, lookup)
            duration_ms: Operation duration in milliseconds
            success: Whether operation succeeded
            document_id: Document ID (optional)
            error_type: Error type if failed (optional)
            metadata: Additional metadata (optional)
        """
        metric = OperationMetric(
            operation_type=operation_type,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            success=success,
            document_id=document_id,
            error_type=error_type,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # Save if storage path configured
        if self.storage_path:
            self._save_metrics()
    
    def get_stats(
        self,
        period_hours: int = 24,
        operation_type: Optional[str] = None
    ) -> UsageStats:
        """
        Get usage statistics for a time period.
        
        Args:
            period_hours: Hours to look back
            operation_type: Filter by operation type (optional)
        
        Returns:
            UsageStats for the period
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(hours=period_hours)
        
        # Filter metrics
        filtered = [
            m for m in self.metrics
            if period_start <= m.timestamp <= period_end
            and (operation_type is None or m.operation_type == operation_type)
        ]
        
        if not filtered:
            return UsageStats(
                period_start=period_start,
                period_end=period_end
            )
        
        # Calculate stats
        total = len(filtered)
        successful = sum(1 for m in filtered if m.success)
        failed = total - successful
        
        signed = sum(1 for m in filtered if m.operation_type == "sign" and m.success)
        verified = sum(1 for m in filtered if m.operation_type == "verify")
        lookups = sum(1 for m in filtered if m.operation_type == "lookup")
        
        avg_duration = sum(m.duration_ms for m in filtered) / total
        error_rate = (failed / total * 100) if total > 0 else 0.0
        
        return UsageStats(
            period_start=period_start,
            period_end=period_end,
            total_operations=total,
            successful_operations=successful,
            failed_operations=failed,
            total_documents_signed=signed,
            total_verifications=verified,
            total_lookups=lookups,
            avg_duration_ms=avg_duration,
            error_rate=error_rate
        )
    
    def get_performance_metrics(
        self,
        period_hours: int = 24,
        operation_type: Optional[str] = None
    ) -> PerformanceMetrics:
        """
        Get performance metrics for a time period.
        
        Args:
            period_hours: Hours to look back
            operation_type: Filter by operation type (optional)
        
        Returns:
            PerformanceMetrics for the period
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(hours=period_hours)
        
        # Filter metrics
        filtered = [
            m for m in self.metrics
            if period_start <= m.timestamp <= period_end
            and (operation_type is None or m.operation_type == operation_type)
        ]
        
        if not filtered:
            return PerformanceMetrics(
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                min_latency_ms=0.0,
                max_latency_ms=0.0,
                avg_latency_ms=0.0
            )
        
        # Sort by duration
        durations = sorted([m.duration_ms for m in filtered])
        
        def percentile(data: List[float], p: float) -> float:
            """Calculate percentile."""
            k = (len(data) - 1) * p
            f = int(k)
            c = int(k) + 1
            if c >= len(data):
                return data[-1]
            return data[f] + (k - f) * (data[c] - data[f])
        
        return PerformanceMetrics(
            p50_latency_ms=percentile(durations, 0.50),
            p95_latency_ms=percentile(durations, 0.95),
            p99_latency_ms=percentile(durations, 0.99),
            min_latency_ms=min(durations),
            max_latency_ms=max(durations),
            avg_latency_ms=sum(durations) / len(durations)
        )
    
    def get_error_breakdown(
        self,
        period_hours: int = 24
    ) -> Dict[str, int]:
        """
        Get breakdown of errors by type.
        
        Args:
            period_hours: Hours to look back
        
        Returns:
            Dict of error_type -> count
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(hours=period_hours)
        
        errors = defaultdict(int)
        
        for metric in self.metrics:
            if (period_start <= metric.timestamp <= period_end
                and not metric.success
                and metric.error_type):
                errors[metric.error_type] += 1
        
        return dict(errors)
    
    def get_hourly_breakdown(
        self,
        period_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get hourly breakdown of operations.
        
        Args:
            period_hours: Hours to look back
        
        Returns:
            List of hourly stats
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(hours=period_hours)
        
        # Group by hour
        hourly = defaultdict(list)
        
        for metric in self.metrics:
            if period_start <= metric.timestamp <= period_end:
                hour = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                hourly[hour].append(metric)
        
        # Calculate stats for each hour
        breakdown = []
        for hour in sorted(hourly.keys()):
            metrics = hourly[hour]
            successful = sum(1 for m in metrics if m.success)
            
            breakdown.append({
                "hour": hour.isoformat(),
                "total_operations": len(metrics),
                "successful": successful,
                "failed": len(metrics) - successful,
                "avg_duration_ms": sum(m.duration_ms for m in metrics) / len(metrics)
            })
        
        return breakdown
    
    def clear_old_metrics(self, days_to_keep: int = 30) -> int:
        """
        Clear metrics older than specified days.
        
        Args:
            days_to_keep: Number of days to retain
        
        Returns:
            Number of metrics removed
        """
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
        original_count = len(self.metrics)
        
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
        
        if self.storage_path:
            self._save_metrics()
        
        return original_count - len(self.metrics)
    
    def _save_metrics(self) -> None:
        """Save metrics to storage."""
        if not self.storage_path:
            return
        
        data = {
            "metrics": [m.to_dict() for m in self.metrics]
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _load_metrics(self) -> None:
        """Load metrics from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.metrics = [
            OperationMetric(
                operation_type=m["operation_type"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
                duration_ms=m["duration_ms"],
                success=m["success"],
                document_id=m.get("document_id"),
                error_type=m.get("error_type"),
                metadata=m.get("metadata", {})
            )
            for m in data.get("metrics", [])
        ]


class DashboardExporter:
    """
    Export metrics to dashboard formats.
    
    Example:
        >>> collector = MetricsCollector()
        >>> exporter = DashboardExporter(collector)
        >>> prometheus_data = exporter.export_prometheus()
    """
    
    def __init__(self, collector: MetricsCollector):
        """
        Initialize dashboard exporter.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector
    
    def export_prometheus(self, period_hours: int = 1) -> str:
        """
        Export metrics in Prometheus format.
        
        Args:
            period_hours: Hours to include
        
        Returns:
            Prometheus-formatted metrics
        """
        stats = self.collector.get_stats(period_hours)
        perf = self.collector.get_performance_metrics(period_hours)
        
        lines = [
            "# HELP encypher_operations_total Total number of operations",
            "# TYPE encypher_operations_total counter",
            f"encypher_operations_total {stats.total_operations}",
            "",
            "# HELP encypher_operations_successful Successful operations",
            "# TYPE encypher_operations_successful counter",
            f"encypher_operations_successful {stats.successful_operations}",
            "",
            "# HELP encypher_operations_failed Failed operations",
            "# TYPE encypher_operations_failed counter",
            f"encypher_operations_failed {stats.failed_operations}",
            "",
            "# HELP encypher_latency_ms Operation latency in milliseconds",
            "# TYPE encypher_latency_ms summary",
            f'encypher_latency_ms{{quantile="0.5"}} {perf.p50_latency_ms}',
            f'encypher_latency_ms{{quantile="0.95"}} {perf.p95_latency_ms}',
            f'encypher_latency_ms{{quantile="0.99"}} {perf.p99_latency_ms}',
            "",
            "# HELP encypher_error_rate Error rate percentage",
            "# TYPE encypher_error_rate gauge",
            f"encypher_error_rate {stats.error_rate}",
        ]
        
        return "\n".join(lines)
    
    def export_json(self, period_hours: int = 24) -> str:
        """
        Export metrics as JSON.
        
        Args:
            period_hours: Hours to include
        
        Returns:
            JSON-formatted metrics
        """
        stats = self.collector.get_stats(period_hours)
        perf = self.collector.get_performance_metrics(period_hours)
        errors = self.collector.get_error_breakdown(period_hours)
        hourly = self.collector.get_hourly_breakdown(period_hours)
        
        data = {
            "usage_stats": stats.to_dict(),
            "performance_metrics": perf.to_dict(),
            "error_breakdown": errors,
            "hourly_breakdown": hourly
        }
        
        return json.dumps(data, indent=2)
    
    def export_grafana(self, period_hours: int = 24) -> Dict[str, Any]:
        """
        Export metrics in Grafana-compatible format.
        
        Args:
            period_hours: Hours to include
        
        Returns:
            Dict with Grafana-formatted data
        """
        hourly = self.collector.get_hourly_breakdown(period_hours)
        
        return {
            "datapoints": [
                {
                    "time": h["hour"],
                    "total_operations": h["total_operations"],
                    "successful": h["successful"],
                    "failed": h["failed"],
                    "avg_duration_ms": h["avg_duration_ms"]
                }
                for h in hourly
            ]
        }


def create_metrics_report(
    collector: MetricsCollector,
    period_hours: int = 24
) -> str:
    """
    Create a formatted metrics report.
    
    Args:
        collector: MetricsCollector instance
        period_hours: Hours to include
    
    Returns:
        Formatted report string
    """
    stats = collector.get_stats(period_hours)
    perf = collector.get_performance_metrics(period_hours)
    errors = collector.get_error_breakdown(period_hours)
    
    report = f"Metrics Report - Last {period_hours} Hours\n"
    report += "=" * 50 + "\n\n"
    
    report += "USAGE STATISTICS:\n"
    report += f"  Total Operations: {stats.total_operations}\n"
    report += f"  Successful: {stats.successful_operations}\n"
    report += f"  Failed: {stats.failed_operations}\n"
    report += f"  Documents Signed: {stats.total_documents_signed}\n"
    report += f"  Verifications: {stats.total_verifications}\n"
    report += f"  Lookups: {stats.total_lookups}\n"
    report += f"  Error Rate: {stats.error_rate:.2f}%\n\n"
    
    report += "PERFORMANCE METRICS:\n"
    report += f"  P50 Latency: {perf.p50_latency_ms:.2f}ms\n"
    report += f"  P95 Latency: {perf.p95_latency_ms:.2f}ms\n"
    report += f"  P99 Latency: {perf.p99_latency_ms:.2f}ms\n"
    report += f"  Min Latency: {perf.min_latency_ms:.2f}ms\n"
    report += f"  Max Latency: {perf.max_latency_ms:.2f}ms\n"
    report += f"  Avg Latency: {perf.avg_latency_ms:.2f}ms\n\n"
    
    if errors:
        report += "ERROR BREAKDOWN:\n"
        for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            report += f"  {error_type}: {count}\n"
    
    return report
