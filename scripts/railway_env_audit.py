#!/usr/bin/env python3
"""
Railway Environment Variable Audit Script

Analyzes service configs to identify required environment variables
and generates Railway CLI commands to set them.
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

SERVICES_DIR = Path(__file__).parent.parent / "services"

# Services currently deployed to Railway
DEPLOYED_SERVICES = [
    "api-gateway",
    "auth-service", 
    "coalition-service",
    "key-service",
    "web-service",
]

# Shared database reference (if using Railway Postgres)
POSTGRES_REF = "${{Postgres.DATABASE_URL}}"
REDIS_REF = "${{Redis.REDIS_URL}}"


def extract_settings_fields(config_path: Path) -> List[Tuple[str, str, bool]]:
    """
    Extract field names, defaults, and required status from a pydantic Settings class.
    Returns list of (field_name, default_value, is_required)
    """
    fields = []
    try:
        content = config_path.read_text(encoding="utf-8")
        
        # Find class Settings block
        # Look for field definitions: FIELD_NAME: type = default or FIELD_NAME: type
        pattern = r'^\s+([A-Z][A-Z0-9_]+):\s*[^=\n]+(?:=\s*(.+))?$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            field_name = match.group(1)
            default_value = match.group(2)
            
            if default_value:
                default_value = default_value.strip().rstrip(',')
                is_required = False
            else:
                default_value = None
                is_required = True
                
            fields.append((field_name, default_value, is_required))
            
    except Exception as e:
        print(f"Error parsing {config_path}: {e}")
    
    return fields


def analyze_service(service_name: str) -> Dict:
    """Analyze a service's config and return env var requirements."""
    config_path = SERVICES_DIR / service_name / "app" / "core" / "config.py"
    
    if not config_path.exists():
        return {"service": service_name, "error": "config.py not found"}
    
    fields = extract_settings_fields(config_path)
    
    required = [(f, d) for f, d, r in fields if r]
    optional = [(f, d) for f, d, r in fields if not r]
    
    return {
        "service": service_name,
        "config_path": str(config_path),
        "required": required,
        "optional": optional,
    }


def generate_railway_commands(analysis: Dict) -> List[str]:
    """Generate railway CLI commands to set variables."""
    commands = []
    service = analysis["service"]
    
    # Required variables
    for field, _ in analysis.get("required", []):
        if "DATABASE" in field or "POSTGRES" in field:
            value = POSTGRES_REF
        elif "REDIS" in field:
            value = REDIS_REF
        else:
            value = f"<SET_{field}>"
        
        commands.append(f'railway variables set {field}="{value}" -s {service}')
    
    return commands


def main():
    print("=" * 60)
    print("Railway Environment Variable Audit")
    print("=" * 60)
    print()
    
    all_commands = []
    
    for service in DEPLOYED_SERVICES:
        analysis = analyze_service(service)
        
        print(f"\n## {service}")
        print("-" * 40)
        
        if "error" in analysis:
            print(f"  ⚠️  {analysis['error']}")
            continue
        
        required = analysis.get("required", [])
        optional = analysis.get("optional", [])
        
        if required:
            print(f"  ❌ REQUIRED ({len(required)}):")
            for field, _ in required:
                print(f"     - {field}")
        else:
            print("  ✅ No required variables (all have defaults)")
        
        if optional:
            print(f"  ℹ️  Optional ({len(optional)}):")
            for field, default in optional[:5]:  # Show first 5
                default_str = str(default)[:30] + "..." if len(str(default)) > 30 else default
                print(f"     - {field} = {default_str}")
            if len(optional) > 5:
                print(f"     ... and {len(optional) - 5} more")
        
        commands = generate_railway_commands(analysis)
        all_commands.extend(commands)
    
    print("\n" + "=" * 60)
    print("Generated Railway CLI Commands")
    print("=" * 60)
    
    if all_commands:
        print("\n# Run these commands to set required variables:")
        for cmd in all_commands:
            print(cmd)
    else:
        print("\n✅ All services have default values - no required variables to set!")
    
    print("\n# Note: Replace <SET_*> placeholders with actual values")
    print("# For database, ensure you have a Postgres service in Railway")
    print("# and use variable references like ${{Postgres.DATABASE_URL}}")


if __name__ == "__main__":
    main()
