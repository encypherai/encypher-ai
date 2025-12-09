#!/usr/bin/env python3
"""
Update Dependencies Script for Encypher Commercial

Updates all services to use consistent, secure dependency versions.

Usage:
    python scripts/update_dependencies.py
"""
import re
from pathlib import Path

# Standardized secure versions for all services
STANDARD_VERSIONS = {
    # Web framework
    "fastapi": ">=0.109.0",
    "uvicorn": ">=0.27.0",
    "uvicorn[standard]": ">=0.27.0",
    
    # Database
    "sqlalchemy": ">=2.0.25",
    "psycopg2-binary": ">=2.9.9",
    "alembic": ">=1.13.0",
    
    # Validation
    "pydantic": ">=2.6.0",
    "pydantic-settings": ">=2.1.0",
    
    # Security
    "cryptography": ">=42.0.0",
    "bcrypt": ">=4.1.0",
    "passlib": ">=1.7.4",
    "passlib[bcrypt]": ">=1.7.4",
    "pyjwt": ">=2.8.0",
    "python-jose": ">=3.3.0",
    "python-jose[cryptography]": ">=3.3.0",
    
    # HTTP
    "httpx": ">=0.27.0",
    
    # Redis
    "redis": ">=5.0.0",
    
    # Templates
    "jinja2": ">=3.1.3",
    
    # Email
    "email-validator": ">=2.1.0",
}

def update_pyproject(filepath: Path) -> int:
    """Update dependencies in a pyproject.toml file."""
    content = filepath.read_text()
    original = content
    changes = 0
    
    for pkg, version in STANDARD_VERSIONS.items():
        # Match patterns like "fastapi>=0.104.0" or "fastapi==0.104.0"
        # Handle packages with extras like "passlib[bcrypt]"
        pkg_escaped = re.escape(pkg)
        pattern = rf'"{pkg_escaped}[<>=!~][^"]*"'
        replacement = f'"{pkg}{version}"'
        
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes += 1
            content = new_content
    
    if changes > 0:
        filepath.write_text(content)
        print(f"  Updated {changes} dependencies")
    else:
        print("  No updates needed")
    
    return changes

def main():
    print("=" * 60)
    print("Updating Dependencies to Secure Versions")
    print("=" * 60)
    
    root = Path(__file__).parent.parent
    total_changes = 0
    
    # Find all pyproject.toml files
    services_dir = root / "services"
    pyproject_files = []
    
    if services_dir.exists():
        for service_dir in services_dir.iterdir():
            if service_dir.is_dir():
                pyproject = service_dir / "pyproject.toml"
                if pyproject.exists():
                    pyproject_files.append(pyproject)
    
    # Add enterprise_api
    enterprise_pyproject = root / "enterprise_api" / "pyproject.toml"
    if enterprise_pyproject.exists():
        pyproject_files.append(enterprise_pyproject)
    
    for pyproject in sorted(pyproject_files):
        service_name = pyproject.parent.name
        print(f"\n{service_name}:")
        changes = update_pyproject(pyproject)
        total_changes += changes
    
    print(f"\n{'='*60}")
    print(f"Total: {total_changes} dependencies updated across {len(pyproject_files)} services")
    print("=" * 60)
    
    if total_changes > 0:
        print("\n⚠️  Remember to rebuild Docker images after updating dependencies!")
        print("   docker-compose -f docker-compose.microservices.yml build")

if __name__ == "__main__":
    main()
