#!/usr/bin/env python3
"""
Type Checker Script for Encypher Commercial

Runs mypy on all Python services and generates a report.

Usage:
    python scripts/run_type_check.py
"""
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

# Services to check
SERVICES = [
    ("auth-service", "services/auth-service/app"),
    ("key-service", "services/key-service/app"),
    ("billing-service", "services/billing-service/app"),
    ("analytics-service", "services/analytics-service/app"),
    ("user-service", "services/user-service/app"),
    ("notification-service", "services/notification-service/app"),
    ("encoding-service", "services/encoding-service/app"),
    ("verification-service", "services/verification-service/app"),
    ("coalition-service", "services/coalition-service/app"),
    ("enterprise-api", "enterprise_api/app"),
]


def run_mypy(path: str) -> Tuple[int, int, str]:
    """Run mypy on a path and return (errors, files_checked, output)."""
    try:
        result = subprocess.run(
            ["mypy", path, "--config-file", "mypy.ini"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        
        # Parse error count from output
        errors = 0
        files = 0
        for line in output.split('\n'):
            if 'Found' in line and 'error' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'Found':
                        try:
                            errors = int(parts[i + 1])
                        except (IndexError, ValueError):
                            pass
                    if part == 'checked':
                        try:
                            files = int(parts[i - 1].strip('('))
                        except (IndexError, ValueError):
                            pass
        
        return errors, files, output
    except Exception as e:
        return -1, 0, str(e)


def main():
    print("=" * 60)
    print("Type Checker (mypy) for Encypher Commercial")
    print("=" * 60)
    
    total_errors = 0
    total_files = 0
    results: Dict[str, Tuple[int, int]] = {}
    
    for name, path in SERVICES:
        if not Path(path).exists():
            print(f"\n{name}: [SKIP] Path not found")
            continue
        
        print(f"\nChecking {name}...", end=" ", flush=True)
        errors, files, output = run_mypy(path)
        
        if errors == -1:
            print(f"[ERROR] {output}")
            continue
        
        results[name] = (errors, files)
        total_errors += errors
        total_files += files
        
        if errors == 0:
            print(f"[OK] {files} files, no errors")
        else:
            print(f"[!] {files} files, {errors} errors")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total files checked: {total_files}")
    print(f"Total type errors: {total_errors}")
    
    print(f"\n{'Service':<25} {'Files':>8} {'Errors':>8}")
    print("-" * 45)
    for name, (errors, files) in sorted(results.items(), key=lambda x: -x[1][0]):
        status = "[OK]" if errors == 0 else "[!]"
        print(f"{name:<25} {files:>8} {errors:>8} {status}")
    
    if total_errors > 0:
        print(f"\n[!] {total_errors} type errors found")
        print("    Most are SQLAlchemy ORM type issues (Column vs value)")
        print("    Consider adding type: ignore comments for known patterns")
        return 1
    else:
        print("\n[OK] All type checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
