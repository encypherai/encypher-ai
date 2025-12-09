#!/usr/bin/env python3
"""
Dependency Audit Script for Encypher Commercial

Checks all services for:
1. Outdated dependencies
2. Known security vulnerabilities
3. Version inconsistencies across services

Usage:
    python scripts/audit_dependencies.py
"""
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Minimum secure versions for critical packages
MINIMUM_VERSIONS = {
    "fastapi": "0.109.0",  # Security fixes
    "uvicorn": "0.27.0",
    "sqlalchemy": "2.0.25",
    "pydantic": "2.6.0",
    "cryptography": "42.0.0",  # Critical security fixes
    "bcrypt": "4.1.0",  # Performance and security
    "httpx": "0.27.0",
    "redis": "5.0.0",
    "psycopg2-binary": "2.9.9",
    "alembic": "1.13.0",
    "jinja2": "3.1.3",  # Security fix
    "pyjwt": "2.8.0",
}

# Known vulnerable versions to flag
VULNERABLE_VERSIONS = {
    "cryptography": ["<41.0.0"],  # CVE-2023-49083
    "jinja2": ["<3.1.3"],  # CVE-2024-22195
    "pydantic": ["<2.5.0"],  # Various fixes
    "bcrypt": ["<4.0.0"],  # Deprecated APIs
}

def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string to tuple for comparison."""
    # Remove operators like >=, ==, etc.
    clean = re.sub(r'^[<>=!~]+', '', version_str.strip())
    # Extract just the version numbers
    match = re.match(r'(\d+)\.(\d+)\.?(\d+)?', clean)
    if match:
        parts = [int(p) for p in match.groups() if p is not None]
        return tuple(parts)
    return (0,)

def version_gte(v1: str, v2: str) -> bool:
    """Check if v1 >= v2."""
    return parse_version(v1) >= parse_version(v2)

def find_pyproject_files() -> List[Path]:
    """Find all pyproject.toml files in services."""
    root = Path(__file__).parent.parent
    files = []
    
    # Check services directory
    services_dir = root / "services"
    if services_dir.exists():
        for service_dir in services_dir.iterdir():
            if service_dir.is_dir():
                pyproject = service_dir / "pyproject.toml"
                if pyproject.exists():
                    files.append(pyproject)
    
    # Check enterprise_api
    enterprise_pyproject = root / "enterprise_api" / "pyproject.toml"
    if enterprise_pyproject.exists():
        files.append(enterprise_pyproject)
    
    return files

def parse_dependencies(pyproject_path: Path) -> Dict[str, str]:
    """Parse dependencies from pyproject.toml."""
    deps = {}
    content = pyproject_path.read_text()
    
    # Find dependencies section
    in_deps = False
    for line in content.split('\n'):
        if 'dependencies = [' in line:
            in_deps = True
            continue
        if in_deps:
            if line.strip() == ']':
                break
            # Parse dependency line like "fastapi>=0.104.0",
            match = re.search(r'"([a-zA-Z0-9_-]+)([<>=!~]+[^"]+)?"', line)
            if match:
                pkg = match.group(1).lower().replace('-', '_').replace('_', '-')
                version = match.group(2) or ""
                deps[pkg] = version
    
    return deps

def check_vulnerabilities(pkg: str, version: str) -> List[str]:
    """Check if package version has known vulnerabilities."""
    issues = []
    pkg_lower = pkg.lower().replace('_', '-')
    
    if pkg_lower in VULNERABLE_VERSIONS:
        for vuln_range in VULNERABLE_VERSIONS[pkg_lower]:
            if vuln_range.startswith('<'):
                max_vuln = vuln_range[1:]
                if version and not version_gte(version.lstrip('>=<!=~'), max_vuln):
                    issues.append(f"Version {version} may be vulnerable (upgrade to >={max_vuln})")
    
    return issues

def check_minimum_version(pkg: str, version: str) -> str:
    """Check if package meets minimum secure version."""
    pkg_lower = pkg.lower().replace('_', '-')
    
    if pkg_lower in MINIMUM_VERSIONS:
        min_ver = MINIMUM_VERSIONS[pkg_lower]
        if version:
            current = version.lstrip('>=<!=~')
            if not version_gte(current, min_ver):
                return f"Recommend upgrading to >={min_ver}"
    
    return ""

def main():
    print("=" * 60)
    print("Encypher Dependency Audit")
    print("=" * 60)
    
    pyproject_files = find_pyproject_files()
    print(f"\nFound {len(pyproject_files)} services to audit\n")
    
    all_deps: Dict[str, Dict[str, str]] = {}  # pkg -> {service: version}
    issues_found = 0
    
    for pyproject in pyproject_files:
        service_name = pyproject.parent.name
        print(f"\n{'='*40}")
        print(f"Service: {service_name}")
        print(f"{'='*40}")
        
        deps = parse_dependencies(pyproject)
        
        for pkg, version in sorted(deps.items()):
            # Track across services
            if pkg not in all_deps:
                all_deps[pkg] = {}
            all_deps[pkg][service_name] = version
            
            # Check for issues
            vulns = check_vulnerabilities(pkg, version)
            recommendation = check_minimum_version(pkg, version)
            
            if vulns or recommendation:
                issues_found += 1
                print(f"\n  ⚠️  {pkg}{version}")
                for v in vulns:
                    print(f"      🔴 VULNERABILITY: {v}")
                if recommendation:
                    print(f"      🟡 {recommendation}")
    
    # Check for version inconsistencies
    print(f"\n{'='*60}")
    print("Version Consistency Check")
    print(f"{'='*60}")
    
    inconsistent = []
    for pkg, services in all_deps.items():
        versions = set(services.values())
        if len(versions) > 1:
            inconsistent.append((pkg, services))
    
    if inconsistent:
        print(f"\n[!] Found {len(inconsistent)} packages with inconsistent versions:\n")
        for pkg, services in inconsistent:
            print(f"  {pkg}:")
            for svc, ver in services.items():
                print(f"    - {svc}: {ver}")
    else:
        print("\n[OK] All packages have consistent versions across services")
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Services audited: {len(pyproject_files)}")
    print(f"Issues found: {issues_found}")
    print(f"Inconsistent versions: {len(inconsistent)}")
    
    if issues_found > 0:
        print("\n[!] Some dependencies need attention!")
        return 1
    else:
        print("\n[OK] All dependencies look good!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
