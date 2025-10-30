"""
Script to add structured logging to all microservices.
"""
import os
import shutil
from pathlib import Path

SERVICES = [
    "user-service",
    "key-service",
    "encoding-service",
    "verification-service",
    "analytics-service",
    "billing-service",
    "notification-service"
]

def add_logging_to_service(service_name):
    """Add structured logging to a service."""
    print(f"📝 Adding structured logging to {service_name}...")
    
    service_path = Path(f"services/{service_name}")
    
    # 1. Add dependencies
    print(f"  Adding dependencies...")
    os.system(f"cd {service_path} && uv add structlog python-json-logger")
    
    # 2. Copy middleware directory from auth-service
    src_middleware = Path("services/auth-service/app/middleware")
    dst_middleware = service_path / "app" / "middleware"
    
    if not dst_middleware.exists():
        print(f"  Copying middleware...")
        shutil.copytree(src_middleware, dst_middleware)
    
    # 3. Copy logging_config from auth-service
    src_logging_config = Path("services/auth-service/app/core/logging_config.py")
    dst_logging_config = service_path / "app" / "core" / "logging_config.py"
    
    print(f"  Copying logging config...")
    shutil.copy2(src_logging_config, dst_logging_config)
    
    # 4. Update main.py
    main_py = service_path / "app" / "main.py"
    content = main_py.read_text()
    
    # Check if already updated
    if "from .core.logging_config import setup_logging" in content:
        print(f"  ⏭️  {service_name} already has structured logging")
        return True
    
    # Replace logging import
    content = content.replace(
        "import logging\n",
        ""
    )
    
    # Add new imports after fastapi imports
    if "from .core.config import settings" in content:
        content = content.replace(
            "from .core.config import settings\n",
            "from .core.config import settings\nfrom .core.logging_config import setup_logging\n"
        )
    
    # Add middleware import
    if "from .monitoring.metrics import setup_metrics" in content:
        content = content.replace(
            "from .monitoring.metrics import setup_metrics\n",
            "from .monitoring.metrics import setup_metrics\nfrom .middleware.logging import RequestLoggingMiddleware\n"
        )
    
    # Replace logging.basicConfig with setup_logging
    content = content.replace(
        'logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))\nlogger = logging.getLogger(__name__)',
        '# Configure structured logging\nlogger = setup_logging(settings.LOG_LEVEL)'
    )
    
    # Add middleware after CORS
    if "# Set up Prometheus metrics" in content:
        content = content.replace(
            "# Set up Prometheus metrics\n",
            "# Add request logging middleware\napp.add_middleware(RequestLoggingMiddleware)\n\n# Set up Prometheus metrics\n"
        )
    
    # Write updated content
    main_py.write_text(content)
    print(f"  ✅ Updated {service_name}/app/main.py")
    
    return True

def main():
    """Main function."""
    print("🚀 Adding structured logging to all services...\n")
    
    base_path = Path(__file__).parent.parent
    os.chdir(base_path)
    
    success_count = 0
    for service_name in SERVICES:
        try:
            if add_logging_to_service(service_name):
                success_count += 1
                print(f"✅ {service_name} complete\n")
        except Exception as e:
            print(f"❌ Error with {service_name}: {e}\n")
    
    print(f"\n✅ Added structured logging to {success_count}/{len(SERVICES)} services!")
    print("\n📝 Next steps:")
    print("1. Test logging: docker-compose -f docker-compose.full-stack.yml up auth-service")
    print("2. Make a request and check logs for JSON format with request_id")
    print("3. Verify X-Request-ID header in responses")

if __name__ == "__main__":
    main()
