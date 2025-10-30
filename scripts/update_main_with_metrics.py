"""
Script to update main.py files to include metrics setup.
"""
from pathlib import Path
import re

SERVICES = [
    "key-service",
    "encoding-service",
    "verification-service",
    "analytics-service",
    "billing-service",
    "notification-service"
]

def update_main_py(service_name):
    """Update main.py to include metrics setup."""
    main_py_path = Path(f"services/{service_name}/app/main.py")
    
    if not main_py_path.exists():
        print(f"❌ {service_name}/app/main.py not found")
        return False
    
    content = main_py_path.read_text()
    
    # Check if already updated
    if "from .monitoring.metrics import setup_metrics" in content:
        print(f"⏭️  {service_name} already has metrics setup")
        return True
    
    # Add import after other imports
    import_pattern = r"(from \.db\.session import engine)"
    import_replacement = r"\1\nfrom .monitoring.metrics import setup_metrics"
    content = re.sub(import_pattern, import_replacement, content)
    
    # Add setup_metrics call after CORS middleware
    setup_pattern = r"(\)\n\napp\.include_router)"
    setup_replacement = r")\n\n# Set up Prometheus metrics\nsetup_metrics(app)\n\napp.include_router"
    content = re.sub(setup_pattern, setup_replacement, content)
    
    # Write updated content
    main_py_path.write_text(content)
    print(f"✅ Updated {service_name}/app/main.py")
    
    return True

def main():
    """Main function."""
    print("🚀 Updating main.py files with metrics setup...\n")
    
    base_path = Path(__file__).parent.parent
    import os
    os.chdir(base_path)
    
    success_count = 0
    for service_name in SERVICES:
        try:
            if update_main_py(service_name):
                success_count += 1
        except Exception as e:
            print(f"❌ Error updating {service_name}: {e}")
    
    print(f"\n✅ Updated {success_count}/{len(SERVICES)} services!")
    print("\n📝 Next steps:")
    print("1. Test each service: cd services/<service-name> && uv run python -m app.main")
    print("2. Check metrics: curl http://localhost:800X/metrics")
    print("3. Start docker-compose with monitoring stack")

if __name__ == "__main__":
    main()
