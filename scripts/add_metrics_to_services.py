"""
Script to add Prometheus metrics to all microservices.
This automates the process of adding monitoring to each service.
"""
import os
from pathlib import Path

# Service configurations with their specific metrics
SERVICES = {
    "key-service": {
        "port": "8003",
        "metrics": [
            ("api_key_operations_total", "Counter", "Total API key operations", "['operation', 'status']"),
            ("key_rotations_total", "Counter", "Total key rotations", "['status']"),
            ("key_validations_total", "Counter", "Total key validations", "['result']"),
            ("active_api_keys", "Gauge", "Number of active API keys", ""),
        ]
    },
    "encoding-service": {
        "port": "8004",
        "metrics": [
            ("documents_signed_total", "Counter", "Total documents signed", "['status']"),
            ("signing_operations_total", "Counter", "Total signing operations", "['operation', 'status']"),
            ("metadata_embedded_total", "Counter", "Total metadata embeddings", "['status']"),
            ("active_signing_operations", "Gauge", "Number of active signing operations", ""),
        ]
    },
    "verification-service": {
        "port": "8005",
        "metrics": [
            ("verifications_total", "Counter", "Total verifications", "['result']"),
            ("signature_validations_total", "Counter", "Total signature validations", "['result']"),
            ("tampering_detected_total", "Counter", "Total tampering detections", ""),
            ("verification_cache_hits", "Counter", "Verification cache hits", ""),
        ]
    },
    "analytics-service": {
        "port": "8006",
        "metrics": [
            ("metrics_recorded_total", "Counter", "Total metrics recorded", "['metric_type']"),
            ("reports_generated_total", "Counter", "Total reports generated", "['report_type']"),
            ("aggregations_total", "Counter", "Total aggregations performed", "['aggregation_type']"),
            ("active_queries", "Gauge", "Number of active queries", ""),
        ]
    },
    "billing-service": {
        "port": "8007",
        "metrics": [
            ("subscriptions_total", "Counter", "Total subscriptions", "['operation', 'status']"),
            ("payments_processed_total", "Counter", "Total payments processed", "['status']"),
            ("invoices_generated_total", "Counter", "Total invoices generated", "['status']"),
            ("active_subscriptions", "Gauge", "Number of active subscriptions", ""),
            ("monthly_revenue", "Gauge", "Monthly revenue in cents", ""),
        ]
    },
    "notification-service": {
        "port": "8008",
        "metrics": [
            ("notifications_sent_total", "Counter", "Total notifications sent", "['channel', 'status']"),
            ("emails_sent_total", "Counter", "Total emails sent", "['status']"),
            ("sms_sent_total", "Counter", "Total SMS sent", "['status']"),
            ("webhooks_delivered_total", "Counter", "Total webhooks delivered", "['status']"),
            ("notification_queue_size", "Gauge", "Size of notification queue", ""),
        ]
    },
}

METRICS_TEMPLATE = '''"""
Prometheus metrics for {service_title}.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info('{service_name}', '{service_title} information')
service_info.info({{
    'version': '1.0.0',
    'service': '{service_name}',
    'port': '{port}'
}})

# Business metrics
{business_metrics}

# System metrics
database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

# Performance metrics
operation_duration = Histogram(
    'operation_duration_seconds',
    'Duration of operations',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Duration of database queries',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)


def setup_metrics(app):
    """
    Set up Prometheus metrics for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Instrumentator instance
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Instrument the app
    instrumentator.instrument(app)
    
    # Expose metrics endpoint
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
    
    return instrumentator
'''

def generate_metric_definition(name, metric_type, description, labels):
    """Generate a metric definition."""
    if labels:
        return f'''{name} = {metric_type}(
    '{name}',
    '{description}',
    {labels}
)'''
    else:
        return f'''{name} = {metric_type}(
    '{name}',
    '{description}'
)'''

def create_metrics_module(service_name, config):
    """Create metrics module for a service."""
    service_title = service_name.replace("-", " ").title()
    
    # Generate business metrics
    business_metrics = "\n\n".join([
        generate_metric_definition(name, mtype, desc, labels)
        for name, mtype, desc, labels in config["metrics"]
    ])
    
    # Generate metrics.py content
    metrics_content = METRICS_TEMPLATE.format(
        service_name=service_name,
        service_title=service_title,
        port=config["port"],
        business_metrics=business_metrics
    )
    
    # Create monitoring directory
    service_path = Path(f"services/{service_name}/app/monitoring")
    service_path.mkdir(parents=True, exist_ok=True)
    
    # Write __init__.py
    (service_path / "__init__.py").write_text('"""Monitoring and observability module."""\n')
    
    # Write metrics.py
    (service_path / "metrics.py").write_text(metrics_content)
    
    print(f"✅ Created metrics module for {service_name}")
    
    return True

def main():
    """Main function to add metrics to all services."""
    print("🚀 Adding Prometheus metrics to all services...\n")
    
    base_path = Path(__file__).parent.parent
    os.chdir(base_path)
    
    for service_name, config in SERVICES.items():
        try:
            create_metrics_module(service_name, config)
        except Exception as e:
            print(f"❌ Error creating metrics for {service_name}: {e}")
    
    print("\n✅ All metrics modules created!")
    print("\n📝 Next steps:")
    print("1. Update each service's main.py to import and call setup_metrics(app)")
    print("2. Test metrics endpoints: curl http://localhost:800X/metrics")
    print("3. Start Prometheus to scrape metrics")

if __name__ == "__main__":
    main()
